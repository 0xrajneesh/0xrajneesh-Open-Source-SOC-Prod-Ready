# Grafana Configuration Guide

## 1. Architecture

```text
Users
  │
  ▼
Grafana :3000
  │
  ├────► Wazuh Indexer / OpenSearch
  │
  └────► Graylog OpenSearch
```

## 2. Recommended Lab Server

```text
OS: Ubuntu 22.04 / 24.04
CPU: 2 vCPU
RAM: 2-4 GB
Disk: 20-30 GB
Example IP: 10.46.96.11
```

Grafana itself does not store the Wazuh or Graylog log data. It queries the configured data sources.

## 3. Required Port

| Port | Purpose |
|---|---|
| `3000/TCP` | Grafana Web UI |
| `9200/TCP` | Outbound connection to OpenSearch |

## 4. Install Grafana

Install prerequisites:

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https wget gnupg
```

Add the Grafana signing key:

```bash
sudo mkdir -p /etc/apt/keyrings

sudo wget -O /etc/apt/keyrings/grafana.asc \
https://apt.grafana.com/gpg-full.key

sudo chmod 644 /etc/apt/keyrings/grafana.asc
```

Add the stable repository:

```bash
echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" | \
sudo tee /etc/apt/sources.list.d/grafana.list
```

Install Grafana OSS:

```bash
sudo apt-get update
sudo apt-get install grafana -y
```

## 5. Start Grafana

```bash
sudo systemctl enable --now grafana-server
```

Verify:

```bash
sudo systemctl status grafana-server
```

## 6. Access Grafana

Open:

```text
http://10.46.96.11:3000
```

The initial local installation commonly uses:

```text
Username: admin
Password: admin
```

Grafana prompts you to change the password after the first login.

## 7. Configure Grafana Server

Main configuration file:

```bash
sudo nano /etc/grafana/grafana.ini
```

Example:

```ini
[server]

http_addr = 0.0.0.0
http_port = 3000
```

Restart:

```bash
sudo systemctl restart grafana-server
```

## 8. Firewall

```bash
sudo ufw allow 3000/tcp
```

Do not expose Grafana directly to the public Internet unless it is appropriately protected.

## 9. Install OpenSearch Data Source Plugin

```bash
sudo grafana-cli plugins install grafana-opensearch-datasource
```

Restart Grafana:

```bash
sudo systemctl restart grafana-server
```

## 10. Add an OpenSearch Data Source

In Grafana:

```text
Connections
   ↓
Add new connection
   ↓
OpenSearch
   ↓
Add new data source
```

You can now create separate data sources for:

```text
Wazuh Indexer
Graylog OpenSearch
```

## 11. Suggested Datasource Layout

```text
Grafana

Datasource 1:
Name: Wazuh-Indexer
Type: OpenSearch
Index: wazuh-alerts-*

Datasource 2:
Name: Graylog-OpenSearch
Type: OpenSearch
Index: graylog_*
```

## 12. Create a Dashboard

Navigate to:

```text
Dashboards
   ↓
New
   ↓
New Dashboard
   ↓
Add visualization
```

Choose the required datasource.

## 13. Recommended SOC Panels

| Panel | Suggested Visualization |
|---|---|
| Total security alerts | Stat |
| Alerts over time | Time series |
| Alerts by severity | Bar chart |
| Top agents | Bar chart |
| Top source IPs | Table |
| Authentication failures | Time series |
| Firewall denies | Time series |
| Graylog events | Stat |
| Wazuh alerts | Stat |
| Top event sources | Table |

## 14. Verify Grafana

Check listening port:

```bash
sudo ss -lntp | grep 3000
```

Check service:

```bash
sudo systemctl status grafana-server
```

Follow logs:

```bash
sudo journalctl -u grafana-server -f
```

## Final Flow

```text
Wazuh Indexer ──────┐
                    │
                    ▼
                 Grafana
                    ▲
                    │
Graylog OpenSearch ─┘
```

## References

- Grafana Ubuntu/Debian installation:
  https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/

- Grafana OpenSearch datasource:
  https://grafana.com/docs/plugins/grafana-opensearch-datasource/latest/
