#!/bin/bash
# Wazuh active response :: network isolation for a compromised Linux endpoint.
#
# Applies a deny-all firewall policy with a narrow allowlist so the SOC keeps
# management access while the host is cut off from everything else.
#
# Install on the AGENT:
#   cp isolate-host.sh /var/ossec/active-response/bin/isolate-host
#   chmod 750 /var/ossec/active-response/bin/isolate-host
#   chown root:wazuh /var/ossec/active-response/bin/isolate-host
#
# Manager ossec.conf:
#   <command>
#     <name>isolate-host</name>
#     <executable>isolate-host</executable>
#     <timeout_allowed>yes</timeout_allowed>
#   </command>
#   <active-response>
#     <command>isolate-host</command>
#     <location>local</location>
#     <rules_id>160102,160107</rules_id>
#     <timeout>3600</timeout>
#   </active-response>
#
# Isolation is disruptive. Keep ISOLATION_ENABLED=no until the SOC has signed off
# on the allowlist, and drive it manually from n8n (auto-containment workflow)
# with a human approval step in front.

set -euo pipefail

ISOLATION_ENABLED="no"
ALLOWED_MGMT_CIDR="10.10.0.0/24"     # SOC jump hosts and Wazuh manager
WAZUH_MANAGER_IP="10.10.0.11"
LOG="/var/ossec/logs/active-responses.log"
STATE="/var/ossec/var/run/isolation.state"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') isolate-host: $*" >>"$LOG"; }

read -r INPUT || INPUT=""
ACTION=$(echo "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
ACTION=${ACTION:-${1:-add}}

if [ "$ISOLATION_ENABLED" != "yes" ]; then
  log "DRY RUN action=$ACTION - isolation disabled in script config, no changes made"
  exit 0
fi

backend() {
  if command -v nft >/dev/null 2>&1; then echo nft
  elif command -v iptables >/dev/null 2>&1; then echo iptables
  else echo none; fi
}

isolate_nft() {
  nft list table inet wazuh_isolation >/dev/null 2>&1 && nft delete table inet wazuh_isolation
  nft add table inet wazuh_isolation
  nft add chain inet wazuh_isolation input '{ type filter hook input priority -10 ; policy drop ; }'
  nft add chain inet wazuh_isolation output '{ type filter hook output priority -10 ; policy drop ; }'
  nft add rule inet wazuh_isolation input ct state established,related accept
  nft add rule inet wazuh_isolation input ip saddr "$ALLOWED_MGMT_CIDR" accept
  nft add rule inet wazuh_isolation output ip daddr "$ALLOWED_MGMT_CIDR" accept
  nft add rule inet wazuh_isolation output ip daddr "$WAZUH_MANAGER_IP" accept
  nft add rule inet wazuh_isolation input iif lo accept
  nft add rule inet wazuh_isolation output oif lo accept
}

restore_nft() {
  nft list table inet wazuh_isolation >/dev/null 2>&1 && nft delete table inet wazuh_isolation
}

isolate_iptables() {
  iptables -N WAZUH_ISOLATION 2>/dev/null || iptables -F WAZUH_ISOLATION
  iptables -A WAZUH_ISOLATION -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  iptables -A WAZUH_ISOLATION -s "$ALLOWED_MGMT_CIDR" -j ACCEPT
  iptables -A WAZUH_ISOLATION -d "$ALLOWED_MGMT_CIDR" -j ACCEPT
  iptables -A WAZUH_ISOLATION -d "$WAZUH_MANAGER_IP" -j ACCEPT
  iptables -A WAZUH_ISOLATION -i lo -j ACCEPT
  iptables -A WAZUH_ISOLATION -j DROP
  iptables -I INPUT 1 -j WAZUH_ISOLATION
  iptables -I OUTPUT 1 -j WAZUH_ISOLATION
}

restore_iptables() {
  iptables -D INPUT -j WAZUH_ISOLATION 2>/dev/null || true
  iptables -D OUTPUT -j WAZUH_ISOLATION 2>/dev/null || true
  iptables -F WAZUH_ISOLATION 2>/dev/null || true
  iptables -X WAZUH_ISOLATION 2>/dev/null || true
}

case "$ACTION" in
  add)
    case "$(backend)" in
      nft)      isolate_nft ;;
      iptables) isolate_iptables ;;
      *)        log "ERROR no supported firewall backend found"; exit 1 ;;
    esac
    date -u +%FT%TZ >"$STATE"
    log "host isolated, management access retained for $ALLOWED_MGMT_CIDR"
    ;;
  delete)
    case "$(backend)" in
      nft)      restore_nft ;;
      iptables) restore_iptables ;;
    esac
    rm -f "$STATE"
    log "isolation lifted, normal connectivity restored"
    ;;
  *)
    log "unknown action: $ACTION"
    exit 1
    ;;
esac
