# Graylog Configuration Guide

This guide uses a simple lab deployment with Graylog Open, MongoDB, and a self-managed OpenSearch node running through Docker Compose.

## 1. Architecture

```text
Log Sources
    │
    ▼
Graylog
    │
    ├────► MongoDB
    │      Configuration / metadata
    │
    └────► OpenSearch
           Log storage / search
```

## 2. Recommended Lab Server

```text
OS: Ubuntu 22.04 / 24.04
CPU: 4 vCPU
RAM: 8 GB minimum
Disk: 100 GB+
Example IP: 10.46.96.9
```

For larger deployments, size OpenSearch primarily according to ingestion rate, retention, replica count, and search load.

## 3. Required Ports

| Port | Purpose |
|---|---|
| `9000/TCP` | Graylog Web UI and REST API |
| `5140/UDP` | Syslog UDP input |
| `5140/TCP` | Syslog TCP input |
| `5044/TCP` | Beats input |
| `12201/UDP` | GELF UDP |
| `12201/TCP` | GELF TCP |
| `9200/TCP` | OpenSearch API |
| `27017/TCP` | MongoDB — normally keep internal only |

Only expose the ports you actually require.

## 4. Install Docker

```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin -y

sudo systemctl enable --now docker
```

Verify:

```bash
docker --version
docker compose version
```

## 5. OpenSearch Host Requirement

Set `vm.max_map_count`:

```bash
sudo sysctl -w vm.max_map_count=262144
```

Make it persistent:

```bash
echo "vm.max_map_count=262144" | \
sudo tee /etc/sysctl.d/99-opensearch.conf

sudo sysctl --system
```

## 6. Create Graylog Directory

```bash
mkdir -p ~/graylog
cd ~/graylog
```

## 7. Generate Graylog Secrets

Generate a password secret:

```bash
openssl rand -base64 48
```

Save the result.

Generate the SHA-256 hash for your Graylog admin password:

```bash
echo -n "YOUR_ADMIN_PASSWORD" | sha256sum
```

Copy only the hash.

## 8. Create Docker Compose File

Create:

```bash
nano docker-compose.yml
```

Example:

```yaml
services:

  mongodb:
    image: mongo:7.0
    container_name: graylog-mongodb
    restart: unless-stopped
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
    networks:
      - graylog

  opensearch:
    image: opensearchproject/opensearch:2.19.5
    container_name: graylog-opensearch
    restart: unless-stopped

    environment:
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - action.auto_create_index=false
      - plugins.security.disabled=true
      - plugins.security.ssl.http.enabled=false
      - OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g
      - OPENSEARCH_INITIAL_ADMIN_PASSWORD=CHANGE_ME_STRONG_PASSWORD

    ulimits:
      memlock:
        soft: -1
        hard: -1

      nofile:
        soft: 65536
        hard: 65536

    volumes:
      - opensearch_data:/usr/share/opensearch/data

    ports:
      - "9200:9200"

    networks:
      - graylog

  graylog:
    image: graylog/graylog:7.1
    container_name: graylog
    restart: unless-stopped

    depends_on:
      - mongodb
      - opensearch

    entrypoint:
      /usr/bin/tini -- wait-for-it opensearch:9200 -- /docker-entrypoint.sh

    environment:
      GRAYLOG_PASSWORD_SECRET: "REPLACE_WITH_GENERATED_SECRET"
      GRAYLOG_ROOT_PASSWORD_SHA2: "REPLACE_WITH_ADMIN_PASSWORD_HASH"

      GRAYLOG_HTTP_BIND_ADDRESS: "0.0.0.0:9000"
      GRAYLOG_HTTP_EXTERNAL_URI: "http://10.46.96.9:9000/"

      GRAYLOG_MONGODB_URI: "mongodb://mongodb:27017/graylog"
      GRAYLOG_ELASTICSEARCH_HOSTS: "http://opensearch:9200"

    ports:
      - "9000:9000/tcp"

      - "5140:5140/tcp"
      - "5140:5140/udp"

      - "5044:5044/tcp"

      - "12201:12201/tcp"
      - "12201:12201/udp"

    volumes:
      - graylog_data:/usr/share/graylog/data

    networks:
      - graylog

networks:
  graylog:
    driver: bridge

volumes:
  mongodb_data:
  mongodb_config:
  opensearch_data:
  graylog_data:
```

> This is a lab-friendly configuration. OpenSearch security is disabled here to simplify the integration. Do not expose port `9200` to untrusted networks.

## 9. Start Graylog

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

Logs:

```bash
docker compose logs -f graylog
```

## 10. Access Graylog

Open:

```text
http://10.46.96.9:9000
```

Login:

```text
Username: admin
Password: the password used when creating GRAYLOG_ROOT_PASSWORD_SHA2
```

## 11. Create a Syslog Input

In Graylog:

```text
System
  ↓
Inputs
  ↓
Select Input
  ↓
Syslog UDP
  ↓
Launch New Input
```

Configure:

```text
Title: Wazuh Syslog
Bind address: 0.0.0.0
Port: 5140
Global: Enabled
```

Start the input.

## 12. Verify the Input Port

```bash
sudo ss -lunp | grep 5140
```

For TCP:

```bash
sudo ss -lntp | grep 5140
```

## 13. Send a Test Syslog Message

From another Linux host:

```bash
echo '<13>Test Graylog message' | nc -u 10.46.96.9 5140
```

Search in Graylog:

```text
Search
```

You should see the test message.

## 14. Verify OpenSearch

```bash
curl http://10.46.96.9:9200
```

List indices:

```bash
curl "http://10.46.96.9:9200/_cat/indices?v"
```

Graylog index names commonly begin with a Graylog index-set prefix. Use the actual index name shown by `_cat/indices` when configuring Grafana.

## 15. Useful Docker Commands

Status:

```bash
docker compose ps
```

Restart:

```bash
docker compose restart
```

Stop:

```bash
docker compose down
```

Follow logs:

```bash
docker compose logs -f
```

## Version Note

Graylog 7.1 supports MongoDB 7.x through 8.2.x and self-managed OpenSearch up to 2.19.5. OpenSearch 3.x is not supported by Graylog 7.1.

## References

- Graylog Docker installation with self-managed OpenSearch:
  https://go2docs.graylog.org/current/downloading_and_installing_graylog/docker_installation_os.htm

- Graylog compatibility matrix:
  https://go2docs.graylog.org/current/downloading_and_installing_graylog/compatibility_matrix.htm

- Graylog inputs:
  https://go2docs.graylog.org/current/getting_in_log_data/inputs.htm
