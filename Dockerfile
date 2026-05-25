# Stage 1: Data Preparation
FROM alpine:latest AS data-prep
WORKDIR /prep
COPY data/Retail_Sales.csv .
COPY data/init.sql .

# Stage 2: Database & Orchestration Image
FROM postgres:14

RUN apt-get update -y && \
    apt-get install -y patroni python3-etcd curl jq && \
    rm -rf /var/lib/apt/lists/*

COPY --from=data-prep /prep/Retail_Sales.csv /tmp/Retail_Sales.csv
COPY --from=data-prep /prep/init.sql /tmp/init.sql

RUN chmod +x /usr/bin/patroni

# --- SỬA Ở ĐÂY ---
# Cấp quyền sở hữu các file data cho user postgres
RUN chown postgres:postgres /tmp/Retail_Sales.csv /tmp/init.sql
# Bắt buộc container phải chạy bằng user postgres thay vì root
USER postgres
# -----------------

ENTRYPOINT ["/usr/bin/patroni", "/etc/patroni/patroni.yml"]