# Cloud Detection Rules

## Purpose

This folder stores detections for cloud control plane and cloud-native audit events.

## Priority Detection Themes

- IAM abuse
- Suspicious console logins
- Token misuse
- Policy changes
- Storage exposure
- Logging disablement
- Security group or firewall weakening

## Design Guidance

- Model rule logic around identity, source, action, and resource sensitivity.
- Elevate severity when security controls are disabled or weakened.
- Preserve cloud account ID, principal, region, and resource identifiers for enrichment.
- Group by provider if multi-cloud support is added later.

## Suggested File Layout

```text
aws-iam-abuse.xml
aws-logging-disable.xml
aws-storage-exposure.xml
generic-cloud-admin-abuse.xml
```
