import psycopg2
import time
import datetime
import random

# Cấu hình kết nối vào HAProxy (Cổng 5000 - Write)
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "127.0.0.1",
    "port": "5000",
    "connect_timeout": 2
}

def test_failover():
    print("--- BẮT ĐẦU TEST FAILOVER (RETAIL SALES) ---")
    print("Mẹo: Hãy qua Terminal khác và gõ lệnh: docker kill <tên_primary_node>")
    
    is_down = False
    start_downtime = None

    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Thay vì SELECT now(), ta thực hiện INSERT để chứng minh quyền Ghi
            dummy_price = round(random.uniform(10.0, 500.0), 2)
            cur.execute(
                f"INSERT INTO retail_sales (date, customer_id, product_category, quantity, price) "
                f"VALUES (CURRENT_DATE, 'TEST-CUST', 'Test Failover', 1, {dummy_price});"
            )
            conn.commit() # Xác nhận lưu vào DB
            
            cur.close()
            conn.close()

            if is_down:
                end_downtime = time.time()
                failover_time = end_downtime - start_downtime
                print(f"\n[PHỤC HỒI] Ghi dữ liệu thành công! Node Primary mới đã lên.")
                print(f"=====================================")
                print(f"🔥 FAILOVER TIME: {failover_time:.2f} GIÂY 🔥")
                print(f"=====================================")
                break 
            else:
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - WRITE OK: Đã thêm 1 đơn hàng giả.")
                time.sleep(0.5)

        except Exception as e:
            if not is_down:
                print(f"\n[SỰ CỐ] Mất kết nối Write! Bắt đầu đếm thời gian downtime...")
                start_downtime = time.time()
                is_down = True
            
            print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - FAILED: Đang chờ Patroni bầu Leader mới...")
            time.sleep(0.5)

if __name__ == "__main__":
    test_failover()