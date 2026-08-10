# Open Source SOC Production

<p align="center">
  <img src="https://img.shields.io/badge/Wazuh-Cluster-0266C8?style=for-the-badge&logo=wazuh&logoColor=white" alt="Wazuh Cluster" />
  <img src="https://img.shields.io/badge/Graylog-Log%20Engineering-FF3633?style=for-the-badge&logo=graylog&logoColor=white" alt="Graylog" />
  <img src="https://img.shields.io/badge/Grafana-Visibility-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana" />
  <img src="https://img.shields.io/badge/n8n-Automation-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" alt="n8n" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Open%20Source-SOC-111827?style=flat-square" alt="Open Source SOC" />
  <img src="https://img.shields.io/badge/Focus-Custom%20Rules%20%26%20Automations-0F766E?style=flat-square" alt="Focus Custom Rules and Automations" />
  <img src="https://img.shields.io/badge/Deployment-Server%20Nodes-7C3AED?style=flat-square" alt="Deployment Server Nodes" />
  <img src="https://img.shields.io/badge/Status-Documentation%20in%20Progress-F59E0B?style=flat-square" alt="Documentation in Progress" />
</p>

This repository is the source of truth for a custom open-source SOC stack built on a **Wazuh cluster**, **Graylog**, **Grafana**, and **n8n** running on **server nodes**, not Kubernetes.

The goal is to version the parts that actually matter for SOC engineering:

- Custom Wazuh rules, decoders, and lists
- Custom Graylog pipelines, streams, and alerts
- Custom Grafana dashboards and alert logic
- Custom n8n workflows and response automations
- Shared schemas, mappings, and validation assets

It does **not** try to duplicate vendor documentation or basic setup steps already covered on official product websites.

## Block Diagram

```mermaid
flowchart LR
    A["Endpoints / Servers / Network Devices"] --> B["Wazuh Agents"]
    B --> C["Wazuh Cluster"]
    C --> D["Custom Rules"]
    C --> E["Custom Decoders"]
    C --> F["Custom Lists"]

    C --> G["Graylog"]
    G --> H["Pipelines"]
    G --> I["Streams"]
    G --> J["Alerts"]

    C --> K["Grafana Dashboards"]
    G --> K

    C --> L["n8n Automations"]
    G --> L
    K --> L

    L --> M["Enrichment"]
    L --> N["Notification"]
    L --> O["Ticketing / Response"]
```

## What This Repo Stores

### Included

- Detection engineering content
- Parsing and enrichment logic
- SOC dashboards and analyst views
- Automation workflows and integration glue
- Shared testing and normalization assets

### Not Included

- Default vendor configuration copied as-is
- Basic installation instructions from official docs
- Real credentials, keys, or secrets
- Uncurated exports with no operational value

## Repository Layout

```text
docs/        Architecture, node layout, data flow, and integration design
wazuh/       Custom detections, decoders, lists, integrations, and scripts
graylog/     Custom pipelines, streams, alerts, dashboards, and scripts
grafana/     Custom dashboards, panels, alert rules, and query patterns
n8n/         Custom workflows, subworkflows, payload examples, and scripts
shared/      Shared schemas, mappings, normalization patterns, and helpers
use-cases/   Detection and response scenarios mapped across multiple tools
tests/       Validation strategy, sample events, and verification notes
```

## Engineering Principles

- Organize content by tool first.
- Keep only custom and reusable SOC engineering artifacts.
- Make each detection and automation path reviewable in Git.
- Connect use cases across detection, visibility, and response.
- Prefer clear structure over dumping raw exports into the repo.

## Tool Focus

### Wazuh

- Custom rule categories
- Custom decoders
- Threat intel and enrichment integrations
- Cluster sync and health scripts

### Graylog

- Parsing pipelines
- Stream routing
- Enrichment logic
- Analyst alerting content

### Grafana

- SOC overview dashboards
- Detection telemetry
- Analyst reporting views
- Executive summary panels

### n8n

- Alert triage workflows
- Enrichment workflows
- Reporting automations
- Response orchestration playbooks

## Suggested Node Model

```text
Node 1  -> Wazuh master
Node 2  -> Wazuh worker 1
Node 3  -> Wazuh worker 2
Node 4  -> Wazuh indexer or search support
Node 5  -> Graylog
Node 6  -> Grafana
Node 7  -> n8n
```

## Documentation Map

- [Architecture](docs/architecture.md)
- [Data Flow](docs/data-flow.md)
- [Node Layout](docs/node-layout.md)
- [Integration Map](docs/integration-map.md)

## Next Build Steps

1. Finalize node placement and data paths.
2. Define the first real detection use cases.
3. Add custom rules, pipelines, dashboards, and workflows.
4. Add sanitized sample logs and validation assets.
5. Build deployment and health-check scripts around the custom content.

## House of SOC

If you want help setting this up, building new detections, or creating custom automation workflows, contact **House of SOC** at [hi@haxsecurity.com](mailto:hi@haxsecurity.com).
