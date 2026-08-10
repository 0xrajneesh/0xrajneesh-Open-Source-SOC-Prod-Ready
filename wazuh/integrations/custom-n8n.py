#!/usr/bin/env python3
"""
Wazuh integration :: forward alerts to an n8n webhook.

Wazuh's integrator daemon calls this script with:
    argv[1] = path to the alert JSON file
    argv[2] = api_key value from the <integration> block (used here as a shared secret)
    argv[3] = hook_url

Install:
    cp custom-n8n.py /var/ossec/integrations/custom-n8n
    chmod 750 /var/ossec/integrations/custom-n8n
    chown root:wazuh /var/ossec/integrations/custom-n8n

ossec.conf (manager):
    <integration>
      <name>custom-n8n</name>
      <hook_url>https://n8n.soc.internal/webhook/wazuh-alert-triage</hook_url>
      <api_key>REPLACE_WITH_SHARED_SECRET</api_key>
      <level>10</level>
      <alert_format>json</alert_format>
    </integration>

The payload is pre-normalised here rather than in n8n so every downstream workflow
sees the same field names as Graylog and Grafana (see shared/field-mappings/).
"""

import json
import logging
import os
import sys
import time
from urllib import error, request

LOG_FILE = "/var/ossec/logs/integrations.log"
TIMEOUT = 10
RETRIES = 3
BACKOFF = 2

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s custom-n8n %(levelname)s %(message)s",
)


def load_alert(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return json.load(handle)


def dig(obj, *path, default=""):
    """Safe nested lookup: dig(alert, 'rule', 'level')."""
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur if cur is not None else default


def normalise(alert):
    """Map a Wazuh alert onto the shared SOC event schema (shared/schemas/soc-event.schema.json)."""
    rule = alert.get("rule", {}) or {}
    data = alert.get("data", {}) or {}
    agent = alert.get("agent", {}) or {}

    src_ip = data.get("srcip") or dig(data, "win", "eventdata", "ipAddress") or ""
    dst_ip = data.get("dstip") or dig(data, "win", "eventdata", "destinationIp") or ""
    user = (
        data.get("dstuser")
        or data.get("srcuser")
        or dig(data, "win", "eventdata", "targetUserName")
        or ""
    )

    return {
        "schema_version": "1.0",
        "source_tool": "wazuh",
        "event_id": alert.get("id", ""),
        "timestamp": alert.get("timestamp", ""),
        "rule": {
            "id": str(rule.get("id", "")),
            "level": int(rule.get("level", 0) or 0),
            "description": rule.get("description", ""),
            "groups": rule.get("groups", []),
            "mitre_ids": dig(rule, "mitre", "id", default=[]),
            "mitre_tactics": dig(rule, "mitre", "tactic", default=[]),
        },
        "host": {
            "name": agent.get("name", ""),
            "id": agent.get("id", ""),
            "ip": agent.get("ip", ""),
        },
        "source": {"ip": src_ip},
        "destination": {"ip": dst_ip},
        "user": {"name": user},
        "process": {
            "name": dig(data, "win", "eventdata", "image"),
            "command_line": dig(data, "win", "eventdata", "commandLine"),
            "parent_name": dig(data, "win", "eventdata", "parentImage"),
        },
        "file": {"path": alert.get("syscheck", {}).get("path", "")},
        "severity": severity_band(int(rule.get("level", 0) or 0)),
        "raw": alert,
    }


def severity_band(level):
    if level >= 14:
        return "critical"
    if level >= 12:
        return "high"
    if level >= 8:
        return "medium"
    return "low"


def post(url, payload, secret):
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-SOC-Signature": secret,
            "User-Agent": "wazuh-integrator/custom-n8n",
        },
        method="POST",
    )
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            with request.urlopen(req, timeout=TIMEOUT) as resp:
                logging.info(
                    "delivered alert rule=%s status=%s attempt=%s",
                    payload["rule"]["id"],
                    resp.status,
                    attempt,
                )
                return True
        except error.HTTPError as exc:
            last = "HTTP %s %s" % (exc.code, exc.reason)
            if 400 <= exc.code < 500 and exc.code != 429:
                break  # our payload is wrong; retrying will not fix it
        except (error.URLError, OSError) as exc:
            last = str(exc)
        if attempt < RETRIES:
            time.sleep(BACKOFF ** attempt)
    logging.error("delivery failed rule=%s error=%s", payload["rule"]["id"], last)
    return False


def main():
    if len(sys.argv) < 4:
        logging.error("usage: custom-n8n <alert_file> <api_key> <hook_url>")
        return 2

    alert_file, secret, hook_url = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.exists(alert_file):
        logging.error("alert file missing: %s", alert_file)
        return 2

    try:
        payload = normalise(load_alert(alert_file))
    except (ValueError, OSError) as exc:
        logging.error("could not parse alert %s: %s", alert_file, exc)
        return 2

    return 0 if post(hook_url, payload, secret) else 1


if __name__ == "__main__":
    sys.exit(main())
