# Graylog Integration with Grafana

## Goal

Use Grafana to visualize logs stored by Graylog in its self-managed OpenSearch backend.

This guide assumes the lab architecture:

```text
Graylog
   ↓
OpenSearch
   ↓
Grafana OpenSearch Datasource
   ↓
Grafana Dashboards
```

## Architecture

```text
┌─────────────────────────┐
│        Graylog          │
│      10.46.96.9         │
└────────────┬────────────┘
             │
             │ stores messages
             ▼
┌─────────────────────────┐
│  Graylog OpenSearch     │
│      10.46.96.9         │
│        :9200            │
└────────────┬────────────┘
             │
             │ OpenSearch API
             ▼
┌─────────────────────────┐
│        Grafana          │
│     10.46.96.11         │
│        :3000            │
└────────────┬────────────┘
             │
             ▼
        SOC Dashboards
```

> Grafana does not need to query the Graylog web UI. It queries the OpenSearch backend that contains the Graylog message indices.

## 1. Verify OpenSearch from Grafana Server

From the Grafana VM:

```bash
curl http://10.46.96.9:9200
```

You should receive OpenSearch cluster information.

List Graylog indices:

```bash
curl "http://10.46.96.9:9200/_cat/indices?v"
```

Identify the index pattern containing Graylog messages.

Example:

```text
graylog_0
graylog_1
graylog_2
```

A useful Grafana pattern may therefore be:

```text
graylog_*
```

Use the actual prefix in your environment.

## 2. Install Grafana OpenSearch Plugin

On the Grafana server:

```bash
sudo grafana-cli plugins install grafana-opensearch-datasource
```

Restart Grafana:

```bash
sudo systemctl restart grafana-server
```

Verify:

```bash
sudo systemctl status grafana-server
```

## 3. Add OpenSearch Data Source

Open Grafana:

```text
http://10.46.96.11:3000
```

Navigate to:

```text
Connections
   ↓
Data sources
   ↓
Add new data source
   ↓
OpenSearch
```

Configure:

```text
Name: Graylog-OpenSearch

URL:
http://10.46.96.9:9200

Access:
Server / Proxy
```

## 4. Configure OpenSearch Settings

Example:

```text
Flavor:
OpenSearch

Version:
2.19.5

Index name:
graylog_*

Time field:
timestamp
```

Important: Graylog message indices commonly use `timestamp` rather than `@timestamp`. Confirm the actual mapping in your environment.

You can inspect a document:

```bash
curl "http://10.46.96.9:9200/graylog_*/_search?size=1&pretty"
```

## 5. Save and Test

Click:

```text
Save & Test
```

Grafana should report a successful connection.

## 6. Test a Query

Create:

```text
Dashboards
  ↓
New Dashboard
  ↓
Add Visualization
  ↓
Graylog-OpenSearch
```

Basic query:

```text
*
```

This should return Graylog data.

## 7. Example Security Queries

All Wazuh-related logs:

```text
message:*Wazuh*
```

Specific host:

```text
source:"wazuh-1"
```

Authentication failures:

```text
message:*failed*
```

Firewall deny events:

```text
action:deny
```

The exact field names depend on the logs and Graylog extractors/pipelines you use.

## 8. Recommended Grafana Panels

A useful SOC dashboard can include:

| Panel | Visualization |
|---|---|
| Total events | Stat |
| Events over time | Time series |
| Events by source | Bar chart |
| Top source IPs | Table / Bar chart |
| Events by severity | Bar chart |
| Wazuh alerts | Time series |
| Firewall denies | Stat / Time series |
| Authentication failures | Time series |
| Top usernames | Table |
| Top destination IPs | Table |

## 9. Example Dashboard Flow

```text
Graylog Logs
     ↓
OpenSearch Index
     ↓
Grafana Query
     ↓
Transform / Aggregate
     ↓
Panel
     ↓
SOC Dashboard
```

## 10. Optional Grafana Provisioning

Grafana supports provisioning the OpenSearch datasource using YAML.

Create:

```bash
sudo nano /etc/grafana/provisioning/datasources/graylog-opensearch.yml
```

Example:

```yaml
apiVersion: 1

datasources:
  - name: Graylog-OpenSearch
    type: grafana-opensearch-datasource
    access: proxy

    url: http://10.46.96.9:9200

    jsonData:
      flavor: opensearch
      version: "2.19.5"
      database: "graylog_*"
      timeField: "timestamp"
      logMessageField: "message"
      pplEnabled: true
      serverless: false

    editable: true
```

Restart:

```bash
sudo systemctl restart grafana-server
```

## 11. Security Recommendation

The lab Docker configuration exposes an unsecured OpenSearch endpoint for simplicity.

Do not expose:

```text
9200/TCP
```

to the Internet or untrusted networks.

In production:

```text
Grafana
   ↓
Authenticated/TLS OpenSearch Endpoint
   ↓
Read-only account
   ↓
Graylog indices
```

Use a dedicated read-only Grafana identity rather than administrative credentials.

## Final Integration

```text
Wazuh
   ↓
Graylog
   ↓
Graylog OpenSearch
   ↓
Grafana OpenSearch Plugin
   ↓
Unified SOC Dashboard
```

## References

- Grafana OpenSearch datasource:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/

- Grafana OpenSearch configuration:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/configure/

- Graylog compatibility matrix:
  https://go2docs.graylog.org/current/downloading_and_installing_graylog/compatibility_matrix.htm
