#!/bin/bash
# post_init.sh - Runs inside the Patroni primary node after bootstrap
echo "=== IMPORT DỮ LIỆU TỰ ĐỘNG ==="
psql -U postgres -d postgres -f /tmp/init.sql
psql -U postgres -d postgres -c "\copy retail_sales (date, customer_id, product_category, quantity, price) FROM '/tmp/Retail_Sales.csv' WITH (FORMAT CSV, HEADER);"

