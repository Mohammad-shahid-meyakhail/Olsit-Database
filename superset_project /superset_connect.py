import psycopg2
import random
import time
from datetime import datetime

# --- Database connection settings ---
DB_CONFIG = {
    "dbname": "olist_db",
    "user": "postgres",
    "password": "99113344",
    "host": "localhost",
    "port": 5432,
}

# --- Connect to database ---
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# --- Auto insert function ---
def insert_new_orders():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Example: Insert new record into 'orders' and 'order_items' tables
            order_id = f"ORDER_{int(datetime.now().timestamp())}"
            customer_id = f"CUST_{random.randint(1000, 9999)}"
            order_status = random.choice(["delivered", "shipped", "processing", "pending"])
            order_purchase_timestamp = datetime.now()

            # Insert into orders
            cur.execute("""
                INSERT INTO orders (order_id, customer_id, order_status, order_purchase_timestamp)
                VALUES (%s, %s, %s, %s)
            """, (order_id, customer_id, order_status, order_purchase_timestamp))

            # Insert into order_items
            product_id = f"PROD_{random.randint(1000, 9999)}"
            seller_id = f"SELL_{random.randint(100, 999)}"
            price = round(random.uniform(20, 500), 2)
            freight_value = round(random.uniform(5, 50), 2)

            cur.execute("""
                INSERT INTO order_items (order_id, product_id, seller_id, price, freight_value)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, product_id, seller_id, price, freight_value))

            conn.commit()
            print(f"✅ New order inserted: {order_id}, Price: {price}, Status: {order_status}")

# --- Main loop ---
def main():
    print("🔄 Auto data insert started (press Ctrl+C to stop)")
    while True:
        insert_new_orders()
        time.sleep(10)  # ⏱ insert new row every 10 seconds

if __name__ == "__main__":
    main()
