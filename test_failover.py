import psycopg
import time
import datetime
import random

# cau hinh ket noi vao cong HA proxy 5000
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "127.0.0.1",
    "port": "5000",
    "connect_timeout": 1
}

def test_failover():
    print("--- BẮT ĐẦU TEST FAILOVER ---")
    
    is_down = False
    start_downtime = None

    while True:
        try:
            conn = psycopg.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            dummy_price = round(random.uniform(10.0, 500.0), 2)
            query = "INSERT INTO retail_sales (date, customer_id, product_category, quantity, price) VALUES (CURRENT_DATE, %s, %s, %s, %s);"
            cur.execute(query, ('TEST-CUST', 'Test Failover psycopg3', 1, dummy_price))
            
            conn.commit() 
            cur.close()
            conn.close()

            if is_down:
                end_downtime = time.time()
                failover_time = end_downtime - start_downtime
                print(f"\n[RECOVER] Ghi dữ liệu thành công! Node Primary đã được bầu.")
                print(f"=====================================")
                print(f"FAILOVER TIME: {failover_time} GIÂY")
                print(f"=====================================")
                break 
            else:
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - WRITE OK: Đã thêm 1 đơn hàng giả.")
                time.sleep(0.5)

        except Exception as e:
            if not is_down:
                print(f"\n[error] Mất kết nối Write! Bắt đầu đếm thời gian downtime...")
                start_downtime = time.time()
                is_down = True
            
            print(".", end="", flush=True)

if __name__ == "__main__":
    test_failover()