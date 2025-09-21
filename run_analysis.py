import psycopg2
import pandas as pd

# Database connection
conn = psycopg2.connect(
    dbname="olist_db",
    user="postgres",       # change if your username is different
    password="your_password", # change this
    host="localhost",
    port="5432"
)

# Read SQL queries from file
with open("analysis_queries.sql", "r") as f:
    queries = f.read().split(";")

# Run queries and save results
for i, query in enumerate(queries):
    q = query.strip()
    if q:  # avoid empty lines
        df = pd.read_sql(q, conn)
        print(f"\nResult {i+1}:")
        print(df.head(), "\n")
        df.to_csv(f"query_result_{i+1}.csv", index=False)

conn.close()
