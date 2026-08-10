# Wazuh to Grafana Dashboard Design

## Objective

Support Grafana dashboards that consume Wazuh-derived security and operational insights.

## Dashboard Inputs

- alert counts by rule group
- alert severity trends
- top affected agents
- authentication anomaly trends
- malware-related alert trends
- rule firing health and noise analysis

## Required Data Consistency

- stable rule group names
- stable severity mapping
- consistent host identity fields
- consistent environment tags

## Visual Targets

- SOC overview
- top noisy detections
- top high-confidence detections
- agent coverage health
- detection drift over time
