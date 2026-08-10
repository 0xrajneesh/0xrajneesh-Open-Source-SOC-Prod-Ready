# Authentication Detection Rules

## Purpose

This folder contains custom detections for identity misuse across Windows, Linux, VPN, SaaS, and authentication infrastructure.

## Priority Detection Themes

- Password spraying
- Brute force attempts
- Impossible travel where relevant
- MFA denial patterns
- Disabled account usage
- New privileged login sources
- Service account abuse

## Detection Guidance

- Build rules that can correlate across different authentication sources.
- Track outcome, username, source address, device, and target service consistently.
- Handle noisy sources separately so real abuse stands out.
- Create severity tiers for failed-only, failed-then-success, and privileged target scenarios.
