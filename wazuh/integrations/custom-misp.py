#!/usr/bin/env python3
"""
Wazuh integration :: MISP IOC lookup.

Takes IP, domain, URL and hash observables out of an alert, asks MISP whether it
knows any of them, and writes a match back into the Wazuh analysis queue so it is
re-evaluated by rules 170010-170012.

Install:
    cp custom-misp.py /var/ossec/integrations/custom-misp
    chmod 750 /var/ossec/integrations/custom-misp
    chown root:wazuh /var/ossec/integrations/custom-misp

ossec.conf (manager):
    <integration>
      <name>custom-misp</name>
      <hook_url>https://misp.internal</hook_url>
      <api_key>REPLACE_WITH_MISP_AUTHKEY</api_key>
      <group>sysmon_event3,sysmon_event_22,web,firewall,syscheck</group>
      <alert_format>json</alert_format>
    </integration>

Design notes:
  - Only observables that can actually be intel-matched are queried; a full alert
    body sent to MISP per event will melt a busy manager.
  - Responses are cached on disk for CACHE_TTL so a beaconing host does not generate
    one MISP query per packet.
  - Private and reserved addresses are never sent off-box.
"""

import hashlib
import ipaddress
import json
import logging
import os
import re
import socket
import ssl
import sys
import time
from urllib import error, request

SOCKET_ADDR = "/var/ossec/queue/sockets/queue"
CACHE_DIR = "/var/ossec/tmp/misp-cache"
CACHE_TTL = 3600
TIMEOUT = 8
VERIFY_TLS = True

logging.basicConfig(
    filename="/var/ossec/logs/integrations.log",
    level=logging.INFO,
    format="%(asctime)s custom-misp %(levelname)s %(message)s",
)

HASH_RE = re.compile(r"^[A-Fa-f0-9]{32}$|^[A-Fa-f0-9]{40}$|^[A-Fa-f0-9]{64}$")
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$")


def is_routable(value):
    try:
        addr = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not (addr.is_private or addr.is_loopback or addr.is_multicast or addr.is_reserved)


def extract_observables(alert):
    data = alert.get("data", {}) or {}
    win = (data.get("win", {}) or {}).get("eventdata", {}) or {}
    syscheck = alert.get("syscheck", {}) or {}

    candidates = [
        data.get("srcip"),
        data.get("dstip"),
        win.get("destinationIp"),
        win.get("queryName"),
        data.get("hostname"),
        syscheck.get("sha256_after"),
        syscheck.get("md5_after"),
        win.get("hashes"),
    ]

    observables = []
    for raw in candidates:
        if not raw or not isinstance(raw, str):
            continue
        for token in re.split(r"[,\s]+", raw.strip()):
            token = token.split("=")[-1].strip().rstrip(".")
            if not token:
                continue
            if is_routable(token) or HASH_RE.match(token) or DOMAIN_RE.match(token):
                observables.append(token)
    return sorted(set(observables))


def cache_path(value):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, hashlib.sha256(value.encode()).hexdigest())


def cache_get(value):
    path = cache_path(value)
    try:
        if time.time() - os.path.getmtime(path) < CACHE_TTL:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
    except (OSError, ValueError):
        pass
    return None


def cache_put(value, result):
    try:
        with open(cache_path(value), "w", encoding="utf-8") as handle:
            json.dump(result, handle)
    except OSError as exc:
        logging.warning("cache write failed: %s", exc)


def misp_lookup(base_url, api_key, value):
    cached = cache_get(value)
    if cached is not None:
        return cached

    payload = json.dumps({"value": value, "limit": 1, "returnFormat": "json"}).encode()
    req = request.Request(
        base_url.rstrip("/") + "/attributes/restSearch",
        data=payload,
        headers={
            "Authorization": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    if not VERIFY_TLS:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    try:
        with request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (error.URLError, error.HTTPError, ValueError, OSError) as exc:
        logging.error("MISP query failed for %s: %s", value, exc)
        return None

    attributes = (body.get("response", {}) or {}).get("Attribute", [])
    result = attributes[0] if attributes else {}
    cache_put(value, result)
    return result


def send_to_analysisd(payload):
    """Re-inject the enriched event so Wazuh rules can alert on it."""
    message = "1:misp:" + json.dumps(payload)
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.connect(SOCKET_ADDR)
        sock.send(message.encode())
        sock.close()
    except OSError as exc:
        logging.error("could not write to analysisd queue: %s", exc)


def main():
    if len(sys.argv) < 4:
        logging.error("usage: custom-misp <alert_file> <api_key> <misp_url>")
        return 2

    alert_file, api_key, misp_url = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(alert_file, "r", encoding="utf-8", errors="replace") as handle:
        alert = json.load(handle)

    agent = alert.get("agent", {}) or {}
    hits = 0

    for observable in extract_observables(alert):
        match = misp_lookup(misp_url, api_key, observable)
        if not match:
            continue
        hits += 1
        send_to_analysisd(
            {
                "integration": "misp",
                "misp": {
                    "value": match.get("value", observable),
                    "category": match.get("category", "unknown"),
                    "type": match.get("type", "unknown"),
                    "event_id": match.get("event_id", ""),
                    "comment": match.get("comment", ""),
                    "to_ids": match.get("to_ids", False),
                },
                "source": {
                    "rule_id": (alert.get("rule", {}) or {}).get("id", ""),
                    "alert_id": alert.get("id", ""),
                },
                "agent": {"name": agent.get("name", ""), "id": agent.get("id", "")},
            }
        )

    logging.info("checked alert %s, %s IOC match(es)", alert.get("id", "?"), hits)
    return 0


if __name__ == "__main__":
    sys.exit(main())
