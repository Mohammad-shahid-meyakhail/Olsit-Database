import psycopg2
import time
from datetime import datetime

# PostgreSQL connection settings
conn = psycopg2.connect(
    host="localhost",
    database="olist_db",    # your database name
    user="postgres",         # your username
    password="99113344", # your PostgreSQL password
)
cursor = conn.cursor()

# Run indefinitely
while True:
    # Example: insert a new order with current timestamp
    query = """
    INSERT INTO orders (order_id, order_purchase_timestamp)
    VALUES (%s, %s)
    """
    new_order_id = "ORDER_" + datetime.now().strftime("%Y%m%d%H%M%S")
    timestamp = datetime.now()

    cursor.execute(query, (new_order_id, timestamp))
    conn.commit()

    print(f"✅ Inserted new order: {new_order_id} at {timestamp}")

    # Wait 10 seconds before inserting the next record
    time.sleep(10)
