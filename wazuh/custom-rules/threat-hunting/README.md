# Threat Hunting Rules

## Purpose

This folder holds lower-confidence, analyst-driven detections designed to support hunting and hypothesis testing.

## Typical Content

- Rare parent-child process chains
- New binary execution from temporary paths
- Unusual administrative tooling
- Scripting interpreter spikes
- Suspicious LOLBin activity

## Guidance

- These rules should be clearly marked as hunt-focused rather than production-blocking.
- Favor rich context and tagging over aggressive severity.
- Document what an analyst should pivot on after the alert fires.
