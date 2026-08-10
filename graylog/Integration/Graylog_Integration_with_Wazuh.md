# Graylog Integration with Wazuh

## Goal

Forward Wazuh security alerts from the Wazuh server cluster to Graylog for centralized search, retention, correlation, and visualization.

## Architecture

```text
Wazuh Agents
     │
     ▼
Load Balancer
     │
     ▼
┌─────────────────────────┐
│ Wazuh Server Cluster    │
│                         │
│ wazuh-1     wazuh-2     │
│ Master       Worker     │
└────────────┬────────────┘
             │
             │ Wazuh Alerts
             │ Syslog UDP :5140
             ▼
┌─────────────────────────┐
│        Graylog          │
│      10.46.96.9         │
│ Syslog Input : 5140     │
└────────────┬────────────┘
             │
             ▼
       Graylog Search
```

Wazuh continues to send its normal alerts to its own Wazuh indexer. Graylog is an additional destination.

## 1. Create Graylog Syslog Input

Log in to Graylog.

Navigate to:

```text
System
  ↓
Inputs
  ↓
Syslog UDP
  ↓
Launch New Input
```

Configure:

```text
Title: Wazuh Alerts
Global: Enabled
Bind address: 0.0.0.0
Port: 5140
Store full message: Enabled
```

Save and start the input.

## 2. Verify Graylog Input

On the Graylog server:

```bash
sudo ss -lunp | grep 5140
```

If Graylog is running in Docker:

```bash
docker ps
```

Confirm that the Graylog container exposes:

```text
5140/udp
```

## 3. Allow Firewall Traffic

On Graylog:

```bash
sudo ufw allow 5140/udp
```

If you use TCP instead:

```bash
sudo ufw allow 5140/tcp
```

## 4. Configure Wazuh Master

Edit:

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Inside the main `<ossec_config>` block add:

```xml
<syslog_output>
  <server>10.46.96.9</server>
  <port>5140</port>
  <level>3</level>
</syslog_output>
```

This example forwards Wazuh alerts at level 3 and above.

If you want only higher-severity alerts:

```xml
<syslog_output>
  <server>10.46.96.9</server>
  <port>5140</port>
  <level>7</level>
</syslog_output>
```

## 5. Configure the Worker Node

In a Wazuh cluster, alerts may be processed on different server nodes depending on the agent connection.

Configure the same `syslog_output` on each Wazuh server that processes agent events.

Example on `wazuh-2`:

```xml
<syslog_output>
  <server>10.46.96.9</server>
  <port>5140</port>
  <level>3</level>
</syslog_output>
```

## 6. Restart Wazuh Manager

On each configured Wazuh server:

```bash
sudo systemctl restart wazuh-manager
```

Verify:

```bash
sudo systemctl status wazuh-manager
```

## 7. Generate a Wazuh Test Alert

You can test Wazuh rule processing using:

```bash
sudo /var/ossec/bin/wazuh-logtest
```

Paste a suitable test event or generate a real test event from an enrolled endpoint.

## 8. Search in Graylog

Open:

```text
http://10.46.96.9:9000
```

Navigate to:

```text
Search
```

Search for:

```text
source:wazuh-1
```

or:

```text
source:wazuh-2
```

You can also search for terms contained in the Wazuh alert message.

## 9. Create a Wazuh Stream

Create a separate Graylog stream for Wazuh alerts:

```text
Streams
  ↓
Create Stream
```

Example:

```text
Title: Wazuh Security Alerts
```

Add a stream rule based on a reliable Wazuh field or source value in your received messages.

This allows separate:

```text
Retention
Dashboards
Alerts
Pipelines
Access Control
```

for Wazuh data.

## 10. Recommended Production Improvement

For a simple lab:

```text
Wazuh → Syslog UDP → Graylog
```

For environments where transport reliability matters, prefer a reliable transport path such as TCP/TLS or an intermediate log forwarder/queue, depending on your architecture.

## Final Flow

```text
Wazuh Agents
      ↓
Wazuh Server Cluster
      │
      ├────────► Wazuh Indexer
      │
      └────────► Graylog Syslog Input
                       ↓
                    Graylog
                       ↓
                  OpenSearch
```

## References

- Wazuh alert forwarding:
  https://documentation.wazuh.com/current/user-manual/manager/alert-management.html

- Wazuh `syslog_output` reference:
  https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/syslog-output.html

- Graylog Syslog inputs:
  https://go2docs.graylog.org/current/getting_in_log_data/syslog_inputs.html
