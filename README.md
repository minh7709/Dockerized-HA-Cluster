# Dockerized-HA-Cluster
Category 13: Cloud-Native Databases (Docker & K8s)
121. Dockerized HA Cluster: "High Availability Retail"
● Dataset: Retail_Sales CSV.
● The Task: Deploy a 3-node PostgreSQL cluster using Docker Compose. Use
HAProxy as a load balancer for read/write splitting.
● Analysis: Simulate a "Container Kill" on the Primary node.
● Metric: Measure the Failover Time—how many seconds of downtime occur before
the Secondary takes over?

sua: patroni:
bootstrap:
  dcs:
    ttl: 10
    loop_wait: 2
    retry_timeout: 5
    postgresql:
      use_pg_rewind: true

sua HAProxy:
default-server inter 1s fall 2 rise 1 on-marked-down shutdown-sessions