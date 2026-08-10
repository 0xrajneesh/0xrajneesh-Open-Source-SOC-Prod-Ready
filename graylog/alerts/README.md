# Alerts

## Purpose

This folder stores Graylog alert strategy and alert object documentation.

## Alert Design Model

- Trigger only when a stream has operational value.
- Prefer threshold or sequence-based conditions over one-off noisy matches.
- Document what severity means for analysts.
- Identify whether the alert should notify, create a ticket, or trigger `n8n`.

## Suggested Alert Families

- repeated auth failures
- brute force followed by success
- malware-related endpoint alert surge
- high-severity Wazuh alert burst
- suspicious internal scanning
