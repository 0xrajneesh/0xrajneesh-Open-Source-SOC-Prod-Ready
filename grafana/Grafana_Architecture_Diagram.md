# Grafana Architecture Diagram

## Architecture

```text
                         ┌─────────────────────┐
                         │       Grafana       │
                         │    10.46.96.11      │
                         │      TCP 3000       │
                         └──────────┬──────────┘
                                    │
                         OpenSearch Datasources
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │   Wazuh Indexer     │           │ Graylog OpenSearch  │
        │      Cluster        │           │    10.46.96.9       │
        │                     │           │      :9200          │
        │ indexer-1           │           └──────────┬──────────┘
        │ indexer-2           │                      │
        │ indexer-3           │                      │
        └──────────┬──────────┘                      │
                   │                                 │
                   │                                 │
        Wazuh Security Alerts                 Graylog Messages
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │ Wazuh Server Cluster│           │       Graylog       │
        │ Master + Worker     │           │    10.46.96.9       │
        └──────────┬──────────┘           └──────────┬──────────┘
                   │                                 │
                   ▼                                 ▼
             Wazuh Agents                    Log Sources
```

## Unified SOC Dashboard Flow

```text
Wazuh Agents
     │
     ▼
Wazuh Servers
     │
     ▼
Wazuh Indexer ───────────────┐
                             │
                             ▼
                          Grafana
                             ▲
                             │
Graylog OpenSearch ──────────┘
     ▲
     │
  Graylog
     ▲
     │
Firewall / Proxy / Linux / Application Logs
```

## Data Sources in Grafana

```text
Grafana
   │
   ├── Datasource 1 ──► Wazuh Indexer
   │                    wazuh-alerts-*
   │
   └── Datasource 2 ──► Graylog OpenSearch
                        graylog_*
```

## Example Node Plan

| Node | Role | Example IP |
|---|---|---|
| `grafana` | Grafana visualization server | `10.46.96.11` |
| `graylog` | Graylog + OpenSearch | `10.46.96.9` |
| `indexer-1` | Wazuh Indexer | `10.46.96.5` |
| `indexer-2` | Wazuh Indexer | `10.46.96.7` |
| `indexer-3` | Wazuh Indexer | `10.46.96.8` |

## Simplified Design

```text
                 ┌───────────────┐
                 │    Grafana    │
                 └───────┬───────┘
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      Wazuh Indexer           Graylog OpenSearch
             ▲                       ▲
             │                       │
          Wazuh                   Graylog
```
