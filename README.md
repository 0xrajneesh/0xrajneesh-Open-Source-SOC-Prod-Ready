
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

<img width="1200" height="794" alt="open source soc" src="https://github.com/user-attachments/assets/e4047ffe-1602-4db3-ad4e-b0dcc0807e89" />

The goal is to version the parts that actually matter for SOC engineering:

- Custom Wazuh rules, decoders, and lists
- Custom Graylog pipelines, streams, and alerts
- Custom Grafana dashboards and alert logic
- Custom n8n workflows and response automations
- Shared schemas, mappings, and validation assets

It does **not** try to duplicate vendor documentation or basic setup steps already covered on official product websites.


## What This Repo Stores

### Included

- Detection engineering content
- Parsing and enrichment logic
- SOC dashboards and analyst views
- Automation workflows and integration glue
- Shared testing and normalization assets



## Documentation Map

- [Architecture](docs/architecture.md)
- [Data Flow](docs/data-flow.md)
- [Node Layout](docs/node-layout.md)
- [Integration Map](docs/integration-map.md)


## House of SOC

If you want help setting this up, building new detections, or creating custom automation workflows, contact **House of SOC** at [hi@haxsecurity.com](mailto:hi@haxsecurity.com).
