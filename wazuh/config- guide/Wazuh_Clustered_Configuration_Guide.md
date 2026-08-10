# Wazuh Clustered Configuration Guide

## Node Plan

  Node          Role              IP
  ------------- ----------------- ---------------
  `indexer-1`   Wazuh Indexer     `10.46.96.5`
  `indexer-2`   Wazuh Indexer     `10.46.96.7`
  `indexer-3`   Wazuh Indexer     `10.46.96.8`
  `wazuh-1`     Wazuh Master      `10.46.96.4`
  `wazuh-2`     Wazuh Worker      `10.46.96.6`
  `dashboard`   Wazuh Dashboard   `10.46.96.3`
  `wazuh-lb`    Load Balancer     `10.46.96.10`

## 1. Required Ports

``` text
1514/TCP       Agent events
1515/TCP       Agent enrollment
1516/TCP       Wazuh server cluster
9200/TCP       Wazuh Indexer API
9300-9400/TCP  Indexer cluster communication
55000/TCP      Wazuh API
443/TCP        Dashboard
```

## 2. Prepare All Nodes

``` bash
sudo apt update && sudo apt upgrade -y
sudo apt install curl unzip tar -y
```

Add to `/etc/hosts`:

``` text
10.46.96.5 indexer-1
10.46.96.7 indexer-2
10.46.96.8 indexer-3
10.46.96.4 wazuh-1
10.46.96.6 wazuh-2
10.46.96.3 dashboard
10.46.96.10 wazuh-lb
```

## 3. Generate Certificates

Run once from `indexer-1`:

``` bash
curl -sO https://packages.wazuh.com/4.14/wazuh-certs-tool.sh
curl -sO https://packages.wazuh.com/4.14/config.yml
nano config.yml
```

Configure:

``` yaml
nodes:
  indexer:
    - name: indexer-1
      ip: "10.46.96.5"
    - name: indexer-2
      ip: "10.46.96.7"
    - name: indexer-3
      ip: "10.46.96.8"

  server:
    - name: wazuh-1
      ip: "10.46.96.4"
      node_type: master
    - name: wazuh-2
      ip: "10.46.96.6"
      node_type: worker

  dashboard:
    - name: dashboard
      ip: "10.46.96.3"
```

Generate:

``` bash
bash wazuh-certs-tool.sh -A
tar -cvf wazuh-certificates.tar -C wazuh-certificates/ .
```

Copy the certificates to the respective nodes.

## 4. Configure Indexer Cluster

Example `/etc/wazuh-indexer/opensearch.yml`:

``` yaml
network.host: "10.46.96.5"
node.name: "indexer-1"
cluster.name: "wazuh-cluster"

cluster.initial_master_nodes:
  - "indexer-1"
  - "indexer-2"
  - "indexer-3"

discovery.seed_hosts:
  - "10.46.96.5"
  - "10.46.96.7"
  - "10.46.96.8"
```

Change `network.host` and `node.name` on each node.

Restart:

``` bash
sudo systemctl restart wazuh-indexer
```

Initialize security once:

``` bash
/usr/share/wazuh-indexer/bin/indexer-security-init.sh
```

Verify:

``` bash
curl -k -u admin https://10.46.96.5:9200/_cluster/health?pretty
```

## 5. Configure Wazuh Server Cluster

Generate a cluster key:

``` bash
openssl rand -hex 16
```

Use the same key on both servers.

### Master --- wazuh-1

Add to `/var/ossec/etc/ossec.conf`:

``` xml
<cluster>
  <name>wazuh</name>
  <node_name>wazuh-1</node_name>
  <node_type>master</node_type>
  <key>YOUR_CLUSTER_KEY</key>
  <port>1516</port>
  <bind_addr>0.0.0.0</bind_addr>
  <nodes>
    <node>10.46.96.4</node>
  </nodes>
  <hidden>no</hidden>
  <disabled>no</disabled>
</cluster>
```

### Worker --- wazuh-2

``` xml
<cluster>
  <name>wazuh</name>
  <node_name>wazuh-2</node_name>
  <node_type>worker</node_type>
  <key>YOUR_CLUSTER_KEY</key>
  <port>1516</port>
  <bind_addr>0.0.0.0</bind_addr>
  <nodes>
    <node>10.46.96.4</node>
  </nodes>
  <hidden>no</hidden>
  <disabled>no</disabled>
</cluster>
```

Restart:

``` bash
sudo systemctl restart wazuh-manager
```

Verify:

``` bash
/var/ossec/bin/cluster_control -l
```

## 6. Configure Filebeat

Configure both Wazuh servers to send alerts to the indexer cluster:

``` yaml
output.elasticsearch.hosts:
  - 10.46.96.5:9200
  - 10.46.96.7:9200
  - 10.46.96.8:9200

output.elasticsearch:
  protocol: https
```

Restart:

``` bash
sudo systemctl restart filebeat
```

## 7. Configure Dashboard

Edit:

``` bash
sudo nano /etc/wazuh-dashboard/opensearch_dashboards.yml
```

Configure:

``` yaml
server.host: 0.0.0.0
server.port: 443

opensearch.hosts:
  - https://10.46.96.5:9200
  - https://10.46.96.7:9200
  - https://10.46.96.8:9200
```

Restart:

``` bash
sudo systemctl restart wazuh-dashboard
```

Access:

``` text
https://10.46.96.3
```

## 8. Configure Load Balancer

Configure the load balancer to forward agent traffic to:

``` text
10.46.96.4:1514
10.46.96.6:1514
```

Agents connect to:

``` text
10.46.96.10:1514
```

## 9. Verify Deployment

Server cluster:

``` bash
/var/ossec/bin/cluster_control -l
```

Indexer cluster:

``` bash
curl -k -u admin https://10.46.96.5:9200/_cluster/health?pretty
```

Services:

``` bash
systemctl status wazuh-manager
systemctl status wazuh-indexer
systemctl status wazuh-dashboard
systemctl status filebeat
```

## Final Flow

``` text
Agents
  ↓
Load Balancer
  ↓
Wazuh Master + Worker
  ↓
Filebeat
  ↓
3-Node Wazuh Indexer Cluster
  ↓
Wazuh Dashboard
```
