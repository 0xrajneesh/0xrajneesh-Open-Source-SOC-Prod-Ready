# Wazuh to Graylog Forwarding

## Objective

Forward selected Wazuh alerts and normalized telemetry into Graylog for parsing, enrichment, stream routing, and long-term analyst workflows.

## Design Goals

- Preserve Wazuh rule ID and rule group context
- Preserve source host and agent identity
- Preserve severity and MITRE mapping where available
- Keep alert payload shape stable for downstream pipelines

## Data Contract

Minimum fields to preserve:

- event timestamp
- wazuh rule ID
- wazuh rule description
- severity
- agent ID
- agent name
- host name
- source IP
- destination IP
- user
- process name
- command line

## Graylog Expectations

- Map Wazuh severity into a consistent operational field.
- Add stream routing for endpoint, authentication, malware, and web categories.
- Enrich alerts with asset criticality and ownership where possible.
