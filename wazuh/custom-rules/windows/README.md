# Windows Detection Rules

## Purpose

This folder is for custom Wazuh rules focused on Windows endpoint telemetry.

## Priority Detection Themes

- Suspicious PowerShell usage
- Encoded command execution
- Privilege escalation behavior
- Defender tampering
- Credential access attempts
- Persistence via scheduled tasks or services
- Lateral movement using native Windows tools

## Suggested File Layout

```text
001-powershell-suspicious.xml
002-credential-access.xml
003-persistence.xml
004-lateral-movement.xml
005-defender-tamper.xml
```

## Detection Guidance

- Prefer high-signal behavior-based detections over single-command string matching.
- Use grouped rules so low-confidence events can roll up into higher-confidence alerts.
- Normalize fields that are reused by Graylog pipelines and Grafana dashboards.
- Keep rule descriptions analyst-readable because they will often appear in alerts and automation payloads.

## Example Coverage Areas

- `powershell.exe -enc`
- `rundll32` misuse
- `regsvr32` remote script execution
- suspicious service creation
- local admin group modification
- unusual use of `net.exe`, `wmic`, `psexec`, or `schtasks`

## Validation Expectations

- Include sample Windows event data in `tests/sample-events/`.
- Document expected rule IDs and severity values.
- Note false-positive conditions for administrative tooling.
