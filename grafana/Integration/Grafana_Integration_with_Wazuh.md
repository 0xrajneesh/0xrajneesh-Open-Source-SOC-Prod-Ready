# Grafana Integration with Wazuh

## Goal

Use Grafana to visualize Wazuh security alerts stored in the Wazuh Indexer.

The Wazuh Indexer is based on OpenSearch, so Grafana can query it using the Grafana OpenSearch datasource.

## Architecture

```text
Wazuh Agents
      │
      ▼
Load Balancer
      │
      ▼
┌───────────────────────────┐
│   Wazuh Server Cluster    │
│                           │
│   Master       Worker     │
└─────────────┬─────────────┘
              │
              │ Filebeat
              ▼
┌───────────────────────────┐
│   Wazuh Indexer Cluster   │
│                           │
│ indexer-1                 │
│ indexer-2                 │
│ indexer-3                 │
│                           │
│ wazuh-alerts-*            │
└─────────────┬─────────────┘
              │
              │ HTTPS :9200
              ▼
┌───────────────────────────┐
│          Grafana          │
│       10.46.96.11         │
│          :3000            │
└───────────────────────────┘
```

## 1. Verify Wazuh Indexer Connectivity

From the Grafana server:

```bash
curl -k https://10.46.96.5:9200
```

Because the Wazuh Indexer normally requires authentication:

```bash
curl -k -u USERNAME:PASSWORD \
https://10.46.96.5:9200/_cluster/health?pretty
```

## 2. Verify Wazuh Indices

```bash
curl -k -u USERNAME:PASSWORD \
"https://10.46.96.5:9200/_cat/indices/wazuh-alerts-*?v"
```

Typical alert pattern:

```text
wazuh-alerts-*
```

Confirm the actual indices before configuring Grafana.

## 3. Install OpenSearch Plugin

On Grafana:

```bash
sudo grafana-cli plugins install grafana-opensearch-datasource
sudo systemctl restart grafana-server
```

## 4. Add Wazuh Indexer Data Source

Navigate to:

```text
Grafana
   ↓
Connections
   ↓
Add new connection
   ↓
OpenSearch
   ↓
Add new data source
```

Configure:

```text
Name:
Wazuh-Indexer

URL:
https://10.46.96.5:9200

Index:
wazuh-alerts-*

Time field:
timestamp
```

Configure the authentication required by your Wazuh Indexer.

For a lab with Wazuh's self-signed certificates, Grafana may also need the Wazuh Indexer CA certificate or an appropriate TLS setting.

## 5. Clustered Wazuh Design

If you have three Wazuh indexers:

```text
10.46.96.5
10.46.96.7
10.46.96.8
```

A better production design is:

```text
Grafana
   ↓
Indexer Load Balancer / Stable Endpoint
   ↓
┌───────────┬───────────┬───────────┐
│ Indexer-1 │ Indexer-2 │ Indexer-3 │
└───────────┴───────────┴───────────┘
```

For a simple lab, Grafana can connect to one healthy Wazuh indexer node because the indexer cluster provides access to the cluster data.

## 6. Save and Test

Click:

```text
Save & Test
```

Grafana should confirm connectivity.

## 7. Test Wazuh Query

Create:

```text
Dashboard
   ↓
Add visualization
   ↓
Wazuh-Indexer
```

Start with:

```text
*
```

## 8. Example Wazuh Queries

High severity alerts:

```text
rule.level:[10 TO *]
```

Authentication-related alerts:

```text
rule.groups:authentication_failed
```

Specific Wazuh agent:

```text
agent.name:"NEX-NYC-LT-001"
```

Specific rule:

```text
rule.id:"5710"
```

Windows events:

```text
decoder.name:"windows_eventchannel"
```

Exact fields depend on your Wazuh alert documents and version.

## 9. Recommended Wazuh Panels

| Panel | Suggested Visualization |
|---|---|
| Total Wazuh alerts | Stat |
| Alerts over time | Time series |
| High severity alerts | Stat |
| Alerts by rule level | Bar chart |
| Top agents | Bar chart |
| Top rules | Table |
| Authentication failures | Time series |
| Windows security alerts | Time series |
| Top source IPs | Table |
| MITRE techniques | Bar chart |

## 10. Suggested Unified Dashboard

```text
┌───────────────────────────────────────────┐
│             SOC OVERVIEW                  │
├──────────────┬──────────────┬─────────────┤
│ Wazuh Alerts │ High Severity│ Graylog Logs│
├──────────────┴──────────────┴─────────────┤
│              Alerts Over Time             │
├─────────────────────┬─────────────────────┤
│ Top Wazuh Agents    │ Top Log Sources     │
├─────────────────────┼─────────────────────┤
│ Top Security Rules  │ Firewall Denies     │
├─────────────────────┴─────────────────────┤
│           Authentication Failures         │
└───────────────────────────────────────────┘
```

## 11. Security Recommendation

Do not use Wazuh Indexer administrator credentials for normal Grafana dashboards.

Recommended:

```text
Grafana
   ↓
Dedicated Read-only User
   ↓
Wazuh Indexer
   ↓
wazuh-alerts-*
```

Grant only the permissions Grafana needs to query the required indices.

## Final Integration

```text
Wazuh Agents
     ↓
Wazuh Server Cluster
     ↓
Wazuh Indexer Cluster
     ↓
Grafana OpenSearch Datasource
     ↓
Wazuh SOC Dashboard
```

## References

- Grafana OpenSearch datasource:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/

- Grafana OpenSearch datasource configuration:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/configure/

- Wazuh Indexer installation/configuration:
  https://documentation.wazuh.com/current/installation-guide/wazuh-indexer/step-by-step.html

- Wazuh OpenSearch integration information:
  https://documentation.wazuh.com/current/integrations-guide/opensearch/index.html
