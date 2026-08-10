# Firewall Detection Rules

## Purpose

This folder is for custom network-edge detections derived from firewall and network security logs.

## Priority Detection Themes

- Port scanning
- Connection bursts
- Denied access to sensitive services
- Geo-based anomalies where relevant
- Repeated outbound beaconing
- Lateral movement across internal segments

## Design Guidance

- Use grouping logic to turn repeated low-level denies into meaningful alerts.
- Separate internet-facing noise from internal misuse.
- Keep asset and segment metadata available for Graylog enrichment.
- Normalize protocol, port, action, source zone, and destination zone fields.

## Example Use Cases

- internal host scanning multiple ports across many destinations
- repeated denied RDP or SSH attempts
- outbound connections to known suspicious destinations
- unusual administrative access between VLANs
