import psycopg2
import re

def get_existing_tables(cur):
    """Fetch all existing table names in the public schema."""
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    return {row[0] for row in cur.fetchall()}

try:
    conn = psycopg2.connect(
        dbname="olist_db",
        user="postgres",
        password="99113344",
        host="127.0.0.1",
        port="5432"
    )
    print("✅ Connection successful!")

    cur = conn.cursor()

    # Get existing tables
    existing_tables = get_existing_tables(cur)
    print(f"📂 Found {len(existing_tables)} tables in DB: {existing_tables}\n")

    # Read SQL file
    with open("analysis_queries.sql", "r") as f:
        sql = f.read()

    # Split queries by semicolon
    queries = [q.strip() for q in sql.split(";") if q.strip()]

    print(f"🔍 Found {len(queries)} queries in the file.\n")

    for i, query in enumerate(queries, start=1):
        # Extract table names with regex (simple version)
        tables_in_query = set(re.findall(r"FROM\s+(\w+)|JOIN\s+(\w+)", query, re.IGNORECASE))
        # Flatten the regex result (list of tuples -> single set)
        tables_in_query = {t for tup in tables_in_query for t in tup if t}

        # Check if all tables exist
        if not tables_in_query.issubset(existing_tables):
            print(f"⚠️ Skipping query {i} (missing tables: {tables_in_query - existing_tables})")
            continue

        print(f"\n▶️ Running query {i}:\n{query}")

        try:
            cur.execute(query)
            try:
                results = cur.fetchall()
                print("📊 Results:")
                for row in results:
                    print(row)
            except psycopg2.ProgrammingError:
                print("ℹ️ Query executed (no results).")
        except Exception as e:
            print(f"❌ Error in query {i}: {e}")

    conn.commit()
    cur.close()
    conn.close()

except Exception as e:
    print("❌ Error:", e)
