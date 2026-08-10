# Wazuh to n8n Triggers

## Objective

Use Wazuh alerts as trigger sources for enrichment, notification, and response workflows in `n8n`.

## High-Value Trigger Categories

- confirmed brute force followed by success
- malware-related detection
- suspicious PowerShell or script execution
- new persistence artifact
- cloud logging disablement
- privileged account abuse

## Payload Guidance

The trigger payload should include:

- unique alert ID
- timestamp
- severity
- rule ID
- rule description
- host or agent identity
- user context
- source and destination IPs
- MITRE tags
- raw event reference

## Automation Ideas

- create ticket
- notify analyst channel
- enrich source IP
- query related Graylog events
- pull recent host timeline
- trigger containment approval workflow
