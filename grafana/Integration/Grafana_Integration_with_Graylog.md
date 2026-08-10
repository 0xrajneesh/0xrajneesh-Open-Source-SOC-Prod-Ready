# Grafana Integration with Graylog

## Goal

Visualize Graylog log data in Grafana.

Grafana queries the OpenSearch backend used by Graylog rather than querying the Graylog Web UI.

## Architecture

```text
Log Sources
     │
     ▼
┌───────────────────────┐
│       Graylog         │
│     10.46.96.9        │
│       :9000           │
└───────────┬───────────┘
            │
            │ stores logs
            ▼
┌───────────────────────┐
│ Graylog OpenSearch    │
│     10.46.96.9        │
│       :9200           │
└───────────┬───────────┘
            │
            │ OpenSearch API
            ▼
┌───────────────────────┐
│       Grafana         │
│    10.46.96.11        │
│       :3000           │
└───────────────────────┘
```

## 1. Verify Graylog OpenSearch

From the Grafana server:

```bash
curl http://10.46.96.9:9200
```

List indices:

```bash
curl "http://10.46.96.9:9200/_cat/indices?v"
```

Identify the Graylog message indices.

Example:

```text
graylog_0
graylog_1
graylog_2
```

Use the actual prefix in your environment.

## 2. Install Grafana OpenSearch Plugin

```bash
sudo grafana-cli plugins install grafana-opensearch-datasource
sudo systemctl restart grafana-server
```

## 3. Add Graylog Data Source

Open Grafana:

```text
http://10.46.96.11:3000
```

Navigate to:

```text
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
Graylog-OpenSearch

URL:
http://10.46.96.9:9200

Index:
graylog_*

Time field:
timestamp
```

Use the actual Graylog index prefix and time field found in your environment.

## 4. Save and Test

Click:

```text
Save & Test
```

Grafana should confirm connectivity to OpenSearch.

## 5. Test Data

Create a new panel and select:

```text
Graylog-OpenSearch
```

Start with:

```text
*
```

This confirms that Grafana can read Graylog messages.

## 6. Example Queries

Specific source:

```text
source:"firewall-01"
```

Authentication failures:

```text
message:*failed*
```

Firewall denies:

```text
action:deny
```

Specific hostname:

```text
source:"server-01"
```

Field names depend on your Graylog parsing and pipelines.

## 7. Recommended Graylog Panels

```text
Total Graylog Events
Events Over Time
Events by Source
Firewall Denies
Authentication Failures
Top Source IPs
Top Destination IPs
Top Users
Top Applications
Top Log Sources
```

## 8. Provision Data Source Using YAML

Create:

```bash
sudo nano /etc/grafana/provisioning/datasources/graylog.yml
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

      database: "graylog_*"

      timeField: "timestamp"

      logMessageField: "message"

    editable: true
```

Restart:

```bash
sudo systemctl restart grafana-server
```

## 9. Production Security

The lab architecture may expose OpenSearch without authentication.

For production use:

```text
Grafana
   ↓
TLS
   ↓
Authenticated OpenSearch
   ↓
Read-only Grafana Account
   ↓
Graylog Indices
```

Grafana should only have the permissions required to read the Graylog indices.

## Final Flow

```text
Firewall / Proxy / Servers
          ↓
       Graylog
          ↓
Graylog OpenSearch
          ↓
       Grafana
          ↓
   SOC Dashboard
```

## References

- Grafana OpenSearch datasource:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/

- Grafana OpenSearch configuration:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/configure/
