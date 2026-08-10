# Web Detection Rules

## Purpose

This folder stores custom detections for web applications, reverse proxies, and web server logs.

## Priority Detection Themes

- Web shell indicators
- Repeated authentication abuse
- Path traversal attempts
- Command injection patterns
- Suspicious user agents
- Exposure scanning and recon
- Abuse of administrative panels

## Design Guidance

- Build layered rules that separate broad recon from confirmed exploitation attempts.
- Reuse lists for blocked paths, admin routes, and suspicious extensions.
- Tune severities using request path, source repetition, and response outcome.
- Preserve source IP, host, URI, method, and response code for downstream enrichment.

## Useful Rule Groupings

- `recon.xml`
- `auth-abuse.xml`
- `rce-patterns.xml`
- `file-access-abuse.xml`
- `web-shell-indicators.xml`

## Validation Expectations

- Test against sanitized access logs from production-like sources.
- Track known noisy scanners separately from real high-priority abuse patterns.
