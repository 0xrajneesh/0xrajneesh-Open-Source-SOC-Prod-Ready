# Wazuh

This folder is for custom Wazuh engineering content only.

## Planned Structure

- `custom-rules/`: custom detection rules by category
- `custom-decoders/`: decoders for unsupported or custom log sources
- `custom-lists/`: lists used by rules or enrichment logic
- `rule-groups/`: grouped detection content for operational organization
- `integrations/`: custom integrations with Graylog, Grafana, and n8n
- `scripts/`: rule deployment, testing, agent health, and cluster sync automation
- `samples/`: sanitized sample logs and expected alert behavior

## Rule Category Examples

- Windows
- Linux
- Web
- Firewall
- Cloud
- Authentication
- Threat hunting
- Malware

## Content Rules

- Store custom logic only.
- Keep sample logs sanitized.
- Document assumptions for each rule set.
