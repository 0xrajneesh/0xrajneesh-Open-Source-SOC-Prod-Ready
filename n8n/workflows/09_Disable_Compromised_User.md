# Disable Compromised User

## Objective

Disable or suspend a user account after high-confidence compromise detection.

## Graylog Event Condition

```text
Confirmed account compromise event
```

## n8n Nodes

1. Webhook
2. Extract username
3. Lookup user
4. Check allowlist/service accounts
5. Approval
6. Identity API — disable user
7. Create Ticket
8. Notify

## Workflow

```text
Graylog Account Compromise
          ↓
        Webhook
          ↓
      Lookup User
          ↓
Service/Privileged Account?
      ┌───┴───┐
     Yes      No
      ↓        ↓
 Escalate   Approval
              ↓
        Disable Account
              ↓
        Ticket + Notify
```

## Configuration Steps

1. Extract the account identifier from the Graylog event.
2. Check whether it is a service, privileged, or break-glass account.
3. Require approval before account disruption.
4. Use Microsoft Graph, Okta, or the relevant identity-provider API to suspend the account.
5. Create an incident ticket.
6. Record who approved the action and the API response.

## Example Incoming Payload

Use this only as a conceptual example. Inspect the real payload Graylog sends to your n8n webhook.

```json
{
  "event": {
    "id": "EVENT-ID",
    "event_definition_id": "DEFINITION-ID",
    "timestamp": "2026-08-10T18:30:00Z",
    "message": "Security event detected",
    "source": "graylog",
    "priority": 4
  },
  "backlog": [
    {
      "source": "host-01",
      "message": "Original event message",
      "src_ip": "203.0.113.10",
      "username": "user1"
    }
  ]
}
```

## Recommended n8n Normalization

Create an **Edit Fields / Set** node immediately after the Webhook and normalize the fields your workflow needs.

Example expressions:

```text
event_id:
{{ $json.body?.event?.id || $json.event?.id }}

event_title:
{{ $json.body?.event?.message || $json.event?.message }}

priority:
{{ $json.body?.event?.priority || $json.event?.priority }}

source:
{{ $json.body?.backlog?.[0]?.source || $json.backlog?.[0]?.source }}

src_ip:
{{ $json.body?.backlog?.[0]?.src_ip || $json.backlog?.[0]?.src_ip }}
```

Adjust these expressions to match your actual Graylog HTTP notification payload.

## Safety / Production Controls

For any workflow that changes infrastructure, identity, endpoint state, firewall policy, or user access:

```text
Detection
   ↓
Validation
   ↓
Enrichment
   ↓
Policy Check
   ↓
Human Approval
   ↓
Response Action
   ↓
Verification
   ↓
Audit Record
```

Recommended controls:

- Never take destructive action from a single unvalidated log message.
- Maintain allowlists for critical assets, administrators, scanners, and service accounts.
- Use dedicated API identities with least privilege.
- Store API keys in n8n Credentials.
- Add timeouts and error handling to all external API calls.
- Record the original Graylog event ID in every ticket/action.
- Require analyst approval for containment in production unless the use case is explicitly pre-authorized.

## Graylog Trigger Setup

Attach an **HTTP Notification** to the relevant Graylog Event Definition.

Example n8n production webhook:

```text
http://10.46.96.12:5678/webhook/graylog-event
```

For production, prefer:

```text
https://n8n.example.com/webhook/graylog-event
```

## References

- n8n Webhook:
  https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/

- Graylog HTTP notifications:
  https://go2docs.graylog.org/current/interacting_with_your_log_data/alert_types.htm
