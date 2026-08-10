# n8n Configuration Guide

## 1. Architecture

```text
                           ┌─────────────────────────┐
                           │        Graylog          │
                           │      10.46.96.9         │
                           │                         │
                           │ Event Definitions       │
                           │ HTTP Notifications      │
                           └────────────┬────────────┘
                                        │
                                        │ HTTP POST
                                        │ Webhook
                                        ▼
                           ┌─────────────────────────┐
                           │          n8n            │
                           │      10.46.96.12        │
                           │        :5678            │
                           └────────────┬────────────┘
                                        │
                     ┌──────────────────┼──────────────────┐
                     │                  │                  │
                     ▼                  ▼                  ▼
                Enrichment          Ticketing          Response
               VirusTotal          Jira/ITSM         Firewall API
               AbuseIPDB           Email/Teams       Endpoint API
               Threat Intel        ServiceNow        AD/Identity
```

## 2. Example Node Plan

| Node | Role | Example IP |
|---|---|---|
| `graylog` | Graylog event source | `10.46.96.9` |
| `n8n` | Automation server | `10.46.96.12` |
| `grafana` | Visualization | `10.46.96.11` |
| `wazuh-1` | Wazuh master | `10.46.96.4` |

## 3. Recommended Lab Resources

```text
OS: Ubuntu 22.04 / 24.04
CPU: 2-4 vCPU
RAM: 4 GB
Disk: 30-50 GB
```

For production, size n8n according to workflow concurrency, payload sizes, execution retention, and external API latency.

## 4. Required Ports

| Port | Purpose |
|---|---|
| `5678/TCP` | n8n Web UI / webhook endpoint |
| `443/TCP` | Recommended external HTTPS endpoint through reverse proxy |
| `80/TCP` | Optional HTTP redirect to HTTPS |

## 5. Install Docker

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin -y

sudo systemctl enable --now docker
```

Verify:

```bash
docker --version
docker compose version
```

## 6. Create n8n Directory

```bash
mkdir -p ~/n8n
cd ~/n8n
```

## 7. Create `.env`

```bash
nano .env
```

Example lab configuration:

```env
N8N_HOST=10.46.96.12
N8N_PORT=5678
N8N_PROTOCOL=http

GENERIC_TIMEZONE=Asia/Kolkata
TZ=Asia/Kolkata

N8N_ENCRYPTION_KEY=REPLACE_WITH_LONG_RANDOM_SECRET
```

Generate a strong encryption key:

```bash
openssl rand -hex 32
```

## 8. Create Docker Compose File

Create:

```bash
nano docker-compose.yml
```

Example:

```yaml
services:

  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    restart: unless-stopped

    ports:
      - "5678:5678"

    environment:
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=${N8N_PORT}
      - N8N_PROTOCOL=${N8N_PROTOCOL}
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE}
      - TZ=${TZ}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}

    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

## 9. Start n8n

```bash
docker compose up -d
```

Verify:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f n8n
```

## 10. Access n8n

Open:

```text
http://10.46.96.12:5678
```

Create the initial owner account.

## 11. Create Graylog Webhook Workflow

In n8n:

```text
Create Workflow
   ↓
Webhook
```

Configure:

```text
HTTP Method: POST
Path: graylog-event
Authentication: Header Auth or Basic Auth recommended
```

n8n provides two URLs:

```text
Test URL
Production URL
```

Use the Test URL while developing.

After activating the workflow, use the Production URL in Graylog.

Example lab URL:

```text
http://10.46.96.12:5678/webhook/graylog-event
```

## 12. Configure Graylog HTTP Notification

In Graylog:

```text
Alerts
   ↓
Notifications
   ↓
Create Notification
   ↓
HTTP Notification
```

Configure:

```text
Title: n8n SOC Automation

URL:
http://10.46.96.12:5678/webhook/graylog-event
```

Graylog sends an HTTP POST request when an attached event definition triggers.

## 13. Test Graylog → n8n

Activate test mode on the n8n Webhook node.

Trigger the Graylog event.

Inspect the incoming JSON under:

```text
Webhook
   ↓
Output
   ↓
JSON
```

The exact Graylog notification payload depends on the event definition and Graylog version.

## 14. Normalize the Graylog Payload

Add an **Edit Fields / Set** node after the Webhook.

Create normalized fields such as:

```text
event_id
event_title
event_definition
priority
timestamp
source
src_ip
dst_ip
username
hostname
rule_id
message
```

Example n8n expression pattern:

```text
{{ $json.body.event.id }}
```

Always inspect your actual webhook payload and adjust field paths accordingly.

## 15. Recommended Base Workflow

```text
Graylog
   ↓
Webhook
   ↓
Normalize Event
   ↓
Validate Required Fields
   ↓
Severity Router
   ↓
Enrichment
   ↓
Decision
   ↓
Response / Ticket / Notification
   ↓
Audit Log
```

## 16. Add Webhook Authentication

Do not leave production SOC automation webhooks unauthenticated.

In the n8n Webhook node use supported authentication such as:

```text
Basic Auth
Header Auth
JWT Auth
```

For Graylog HTTP notification, add the matching authentication/header configuration where supported.

If using a reverse proxy, enforce authentication and TLS there as well.

## 17. Production Reverse Proxy

Recommended production flow:

```text
Graylog
   ↓
HTTPS 443
   ↓
Reverse Proxy
   ↓
n8n :5678
```

When n8n runs behind a reverse proxy, set the externally reachable webhook URL correctly.

Typical variables include:

```env
N8N_HOST=n8n.example.com
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.example.com/
```

Example:

```yaml
environment:
  - N8N_HOST=n8n.example.com
  - N8N_PROTOCOL=https
  - WEBHOOK_URL=https://n8n.example.com/
```

## 18. Firewall

For a private lab:

```bash
sudo ufw allow from 10.46.96.9 to any port 5678 proto tcp
```

This allows Graylog to reach n8n while restricting other sources.

## 19. Credentials

Store external-service secrets using n8n Credentials instead of hard-coding:

```text
VirusTotal API Key
AbuseIPDB API Key
Microsoft Teams / Slack
Jira
ServiceNow
Firewall API
EDR API
Microsoft Graph
SMTP
```

## 20. Execution Retention

SOC workflows can generate many executions.

Review n8n execution retention and pruning settings before production deployment.

Avoid storing sensitive payloads longer than needed.

## 21. Recommended Error Workflow

Create a separate n8n error workflow:

```text
Workflow Error
      ↓
Collect Workflow Name
      ↓
Collect Error
      ↓
Send SOC/Admin Notification
```

This prevents silent automation failures.

## 22. Basic Validation Checklist

```text
[ ] n8n container is running
[ ] Port 5678 is reachable from Graylog
[ ] Graylog HTTP notification exists
[ ] n8n Webhook receives the POST
[ ] Workflow is activated
[ ] Production webhook URL is used
[ ] Credentials are stored securely
[ ] Error handling is configured
[ ] External API calls have timeouts
[ ] Destructive actions require approval
```

## References

- n8n Docker:
  https://docs.n8n.io/hosting/installation/docker/

- n8n Webhook node:
  https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/

- n8n webhook development:
  https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/workflow-development/

- Graylog HTTP notifications:
  https://go2docs.graylog.org/current/interacting_with_your_log_data/alert_types.htm
