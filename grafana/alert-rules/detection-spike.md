# Detection Spike Alert

## Purpose

Alert when a detection category or specific rule group spikes above expected volume.

## Trigger Idea

- compare current window to rolling baseline
- alert only when absolute volume and percent increase both exceed threshold

## Use Cases

- malware surge
- auth failure surge
- web attack burst
