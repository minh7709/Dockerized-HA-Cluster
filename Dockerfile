FROM alpine:latest AS data-prep
WORKDIR /prep
COPY data/Retail_Sales.csv .
COPY data/init.sql .

FROM postgres:14

RUN apt-get update -y && \
    apt-get install -y patroni python3-etcd curl jq && \
    rm -rf /var/lib/apt/lists/*

COPY --from=data-prep /prep/Retail_Sales.csv /tmp/Retail_Sales.csv
COPY --from=data-prep /prep/init.sql /tmp/init.sql

RUN chmod +x /usr/bin/patroni

ENTRYPOINT ["/usr/bin/patroni"]
