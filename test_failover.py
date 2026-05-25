import psycopg2
import time
import datetime


DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "127.0.0.1",
    "port": "5000",
    "connect_timeout": 2
}

def test_failover():
    print("--- BẮT ĐẦU TEST FAILOVER ---")
    print("Mẹo: Hãy qua Terminal khác và gõ lệnh: docker kill <tên_primary_node>")
    
    is_down = False
    start_downtime = None

    while True:
        try:
            # Cố gắng mở kết nối và thực hiện 1 truy vấn
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT now();")
            cur.fetchone()
            cur.close()
            conn.close()

            if is_down:
                # Nếu trước đó đang sập mà giờ kết nối được -> Hệ thống đã phục hồi
                end_downtime = time.time()
                failover_time = end_downtime - start_downtime
                print(f"\n[PHỤC HỒI] Kết nối Write thành công!")
                print(f"=====================================")
                print(f"FAILOVER TIME: {failover_time:.2f} GIÂY")
                print(f"=====================================")
                break
            else:
                print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - OK")
                time.sleep(0.5) 

        except Exception as e:
            if not is_down:
                # Lần đầu tiên phát hiện lỗi
                print(f"\n[SỰ CỐ] Mất kết nối! Bắt đầu đếm thời gian downtime...")
                start_downtime = time.time()
                is_down = True
            
            print(f"{datetime.datetime.now().strftime('%H:%M:%S')} - FAILED: Chờ bầu Leader mới...")
            time.sleep(0.5)

if __name__ == "__main__":
    test_failover()
