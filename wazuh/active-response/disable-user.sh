#!/bin/bash
# Wazuh active response :: disable a local account after confirmed credential abuse.
#
# Scope: local Linux accounts only. Domain accounts are handled by the n8n
# auto-containment workflow calling the identity provider API - never by an
# endpoint script holding directory credentials.
#
# Install on the AGENT:
#   cp disable-user.sh /var/ossec/active-response/bin/disable-user
#   chmod 750 /var/ossec/active-response/bin/disable-user
#   chown root:wazuh /var/ossec/active-response/bin/disable-user
#
# Manager ossec.conf:
#   <command>
#     <name>disable-user</name>
#     <executable>disable-user</executable>
#     <timeout_allowed>yes</timeout_allowed>
#   </command>
#   <active-response>
#     <command>disable-user</command>
#     <location>local</location>
#     <rules_id>100102</rules_id>
#     <timeout>1800</timeout>
#   </active-response>

set -euo pipefail

ENABLED="no"                       # flip to yes only after tabletop testing
PROTECTED_USERS="root|admin|wazuh|ansible|svc_backup"
LOG="/var/ossec/logs/active-responses.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') disable-user: $*" >>"$LOG"; }

read -r INPUT || INPUT=""
ACTION=$(echo "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
USERNAME=$(echo "$INPUT" | sed -n 's/.*"dstuser"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -z "$USERNAME" ] && USERNAME=$(echo "$INPUT" | sed -n 's/.*"srcuser"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
ACTION=${ACTION:-${1:-add}}
USERNAME=${USERNAME:-${3:-}}

if [ -z "$USERNAME" ]; then
  log "no username in alert payload, nothing to do"
  exit 0
fi

if echo "$USERNAME" | grep -qE "^($PROTECTED_USERS)$"; then
  log "REFUSED $USERNAME is on the protected list - escalating to analyst instead"
  exit 0
fi

if ! id "$USERNAME" >/dev/null 2>&1; then
  log "user $USERNAME does not exist locally, nothing to do"
  exit 0
fi

if [ "$ENABLED" != "yes" ]; then
  log "DRY RUN would $ACTION lock on $USERNAME"
  exit 0
fi

case "$ACTION" in
  add)
    passwd -l "$USERNAME" >/dev/null 2>&1 || true
    usermod --expiredate 1 "$USERNAME" >/dev/null 2>&1 || true
    pkill -KILL -u "$USERNAME" >/dev/null 2>&1 || true
    log "locked account $USERNAME and terminated its sessions"
    ;;
  delete)
    passwd -u "$USERNAME" >/dev/null 2>&1 || true
    usermod --expiredate "" "$USERNAME" >/dev/null 2>&1 || true
    log "unlocked account $USERNAME"
    ;;
  *)
    log "unknown action: $ACTION"
    exit 1
    ;;
esac
