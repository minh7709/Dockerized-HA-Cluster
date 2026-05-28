import psycopg
import time
import datetime
import random
import subprocess

# Cấu hình kết nối vào HAProxy cổng 5000 (Primary/Write)
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "127.0.0.1",
    "port": "5000",
    "connect_timeout": 1
}

def get_primary_container_id():
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT pg_read_file('/etc/hostname');")
        container_id = cur.fetchone()[0].strip()
        cur.close()
        conn.close()
        return container_id
    except Exception as e:
        return None

def test_failover():
    print("--- BẮT ĐẦU TEST FAILOVER ---")
    
    auto_id = get_primary_container_id()
    
    if auto_id:
        target_container = auto_id
    else:
        print("[!] Không thể tự động phát hiện node Primary.")
        target_container = input("-> Vui lòng nhập thủ công Container ID hoặc Tên: ").strip()
        if not target_container:
            print("[LỖI] Bạn chưa nhập mục tiêu để kill")
            return

    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        dummy_price = round(random.uniform(10.0, 500.0), 2)
        query = "INSERT INTO retail_sales (date, customer_id, product_category, quantity, price) VALUES (CURRENT_DATE, %s, %s, %s, %s);"
        cur.execute(query, ('TEST-CUST', 'Pre-kill check', 1, dummy_price))
        conn.commit()
        cur.close()
        conn.close()
        print(f" => {datetime.datetime.now().strftime('%H:%M:%S')} - WRITE OK: Đã ghi thành công.")
    except Exception as e:
        print(f"[LỖI] Không thể ghi thử trước khi test: {e}")
        print(" Vui lòng kiểm tra trạng thái cụm database trước.")
        return


    
    try:
        result = subprocess.run(
            ["docker", "kill", target_container],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        start_downtime = time.time()
        print(f" => [OK] Container '{target_container}' đã bị kill thành công.")
    
    except subprocess.CalledProcessError as e:
        print(f"[LỖI] Lệnh docker kill thất bại: {e.stderr.strip()}")
        print(" Hãy đảm bảo Docker đang chạy và bạn nhập đúng ID/Tên.")
        return
    except Exception as e:
        print(f"[LỖI] Không thể thực thi lệnh docker: {e}")
        return

    print("Đang kiểm tra kết nối ghi liên tục mỗi 0.05 giây...")
    
    while True:
        try:
            conn = psycopg.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            dummy_price = round(random.uniform(10.0, 500.0), 2)
            query = "INSERT INTO retail_sales (date, customer_id, product_category, quantity, price) VALUES (CURRENT_DATE, %s, %s, %s, %s);"
            cur.execute(query, ('TEST-CUST', 'Test Failover Recovery', 1, dummy_price))
            conn.commit() 
            cur.close()
            conn.close()

            end_downtime = time.time()
            failover_time = end_downtime - start_downtime
            
            print(f"\n\n[RECOVER] Ghi dữ liệu thành công! Node Primary mới đã được bầu.")
            print(f"====================================================")
            print(f"FAILOVER TIME (DOWNTIME): {failover_time:.4f} GIÂY")
            print(f"====================================================")
            break

        except Exception:
            print(".", end="", flush=True)
            time.sleep(0.05)

if __name__ == "__main__":
    test_failover()