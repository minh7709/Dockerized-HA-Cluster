CREATE TABLE IF NOT EXISTS retail_sales (
    transaction_id SERIAL PRIMARY KEY,
    date DATE,
    customer_id VARCHAR(50),
    product_category VARCHAR(100),
    quantity INT,
    price DECIMAL(10, 2)
);
