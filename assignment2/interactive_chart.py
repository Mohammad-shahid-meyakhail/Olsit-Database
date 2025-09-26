# interactive_chart.py
import psycopg2
import pandas as pd
import plotly.express as px

# --- DB config (same as analytics.py) ---
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "olist_db",   # your database name
    "user": "postgres",     # your postgres username
    "password": "99113344"  # your password
}

# --- Fetch data ---
def fetch_orders():
    query = """
    SELECT DATE(order_purchase_timestamp) as order_date,
           COUNT(order_id) as order_count
    FROM orders
    GROUP BY DATE(order_purchase_timestamp)
    ORDER BY order_date;
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql_query(query, conn)

# --- Main ---
def main():
    df = fetch_orders()

    # Add a 'year_month' column for animation
    df["year_month"] = pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str)

    # Create animated line chart
    fig = px.line(df,
                  x="order_date",
                  y="order_count",
                  animation_frame="year_month",
                  title="Orders Over Time (Interactive Time Slider)",
                  labels={"order_date": "Order Date", "order_count": "Number of Orders"})

    fig.show()

if __name__ == "__main__":
    main()
