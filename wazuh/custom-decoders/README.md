# Custom Decoders

## Purpose

This folder stores custom Wazuh decoders for logs that are not parsed well enough by default.

## Candidate Sources

- Custom application logs
- Reverse proxy logs
- Firewall exports
- VPN logs
- Middleware or API gateway logs
- Security tools with non-standard formats

## Decoder Standards

- Name decoders after the source system.
- Extract stable fields first: timestamp, host, source IP, user, action, status.
- Avoid overfitting to one sample line if formats vary.
- Document the source log format and sample lines beside each decoder set.

## Suggested Structure

```text
app-logs/
firewall/
vpn/
proxy/
```
