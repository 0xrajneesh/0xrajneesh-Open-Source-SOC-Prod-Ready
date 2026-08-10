# Linux Detection Rules

## Purpose

This folder holds custom Wazuh rules for Linux servers and workloads.

## Priority Detection Themes

- Privilege escalation
- SSH brute force and abuse
- Persistence through cron or systemd
- Suspicious shell history patterns
- Reverse shell activity
- Log tampering
- Unauthorized account creation

## Suggested File Layout

```text
001-auth-abuse.xml
002-persistence.xml
003-privilege-escalation.xml
004-reverse-shell.xml
005-defense-evasion.xml
```

## Detection Guidance

- Track both successful and failed activity where chaining matters.
- Prefer detections that combine process, file, and auth context.
- Distinguish admin behavior from attacker tradecraft through path, user, and host role.
- Document distro-specific assumptions when a rule only applies to certain environments.

## Example Coverage Areas

- repeated SSH authentication failures followed by success
- `sudo` abuse from unusual users
- cron job creation in uncommon locations
- modification of `/etc/passwd`, `/etc/shadow`, or sudoers files
- shells spawned by web service accounts

## Validation Expectations

- Map each rule to likely MITRE ATT&CK techniques.
- Include sample logs or command traces when practical.
- Identify operational exceptions for automation or admin scripts.
