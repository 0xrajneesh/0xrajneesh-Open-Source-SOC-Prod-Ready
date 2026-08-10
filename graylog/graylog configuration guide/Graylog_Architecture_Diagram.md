# Graylog Architecture Design

## Architecture

```text
                           ┌─────────────────────────┐
                           │      Log Sources        │
                           │                         │
                           │ Firewall / Proxy / Apps │
                           │ Linux / Network Devices │
                           └────────────┬────────────┘
                                        │
                              Syslog / GELF / Beats
                                        │
                                        ▼
                           ┌─────────────────────────┐
                           │        Graylog          │
                           │       10.46.96.9        │
                           │                         │
                           │ Web / REST API : 9000   │
                           │ Syslog       : 5140     │
                           │ GELF         : 12201    │
                           │ Beats        : 5044     │
                           └───────┬─────────┬───────┘
                                   │         │
                         Metadata  │         │ Search / Logs
                                   ▼         ▼
                         ┌──────────────┐  ┌───────────────────┐
                         │   MongoDB    │  │    OpenSearch     │
                         │ Config/User  │  │ Graylog Log Data  │
                         │   Metadata   │  │      :9200        │
                         └──────────────┘  └─────────┬─────────┘
                                                    │
                                                    │ OpenSearch API
                                                    ▼
                                           ┌───────────────────┐
                                           │      Grafana      │
                                           │    10.46.96.11    │
                                           │       :3000       │
                                           └───────────────────┘
```

## Wazuh + Graylog + Grafana View

```text
                     ┌───────────────────────┐
                     │     Wazuh Agents      │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ Wazuh Server Cluster  │
                     │  Master + Worker      │
                     └───────────┬───────────┘
                                 │
                   Wazuh Alerts  │ Syslog UDP/TCP
                                 ▼
                     ┌───────────────────────┐
                     │       Graylog         │
                     │     10.46.96.9        │
                     │ Syslog Input : 5140   │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ Graylog OpenSearch    │
                     │      :9200            │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │       Grafana         │
                     │ OpenSearch Datasource │
                     └───────────────────────┘
```

## Simplified Flow

```text
Network / Application Logs ───────┐
                                  │
Wazuh Alerts ─────────────────────┼──► Graylog ─► OpenSearch ─► Grafana
                                  │
Linux / Firewall / Proxy Logs ────┘
```

## Example Node Plan

| Node | Role | Example IP |
|---|---|---|
| `graylog` | Graylog + MongoDB + OpenSearch via Docker | `10.46.96.9` |
| `grafana` | Grafana | `10.46.96.11` |
| `wazuh-1` | Wazuh master | `10.46.96.4` |
| `wazuh-2` | Wazuh worker | `10.46.96.6` |

> The IP addresses are example lab addresses and can be changed to match your environment.
