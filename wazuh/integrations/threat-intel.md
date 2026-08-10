# Threat Intelligence Integration

## Objective

Augment Wazuh detections with external or internal threat intelligence without overloading base rules with volatile feeds.

## Integration Patterns

- scheduled list refreshes
- lookup-based match enrichment
- post-alert enrichment in `n8n`
- Graylog lookup correlation for analyst workflows

## Governance

- record feed source
- record update cadence
- define expiration behavior
- distinguish indicator-only matches from confirmed malicious behavior
