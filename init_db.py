import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
import table
load_dotenv(find_dotenv())

TIMESCALE_SERVICE_URL = os.environ.get("TIMESCALE_SERVICE_URL")
if not TIMESCALE_SERVICE_URL:
    print("Error: TIMESCALE_SERVICE_URL environment variable is not set.")
    exit(1)

conn = psycopg2.connect(dsn=TIMESCALE_SERVICE_URL)
cursor = conn.cursor()

# Enable foreign key support (PostgreSQL enforces this by default)
# cursor.execute("PRAGMA foreign_keys = ON;")

# --- SQL Schema Definition ---
schema_sql = table.schema_sql
data_sql = table.data_sql

cursor.execute(schema_sql)
cursor.execute(data_sql)
conn.commit()

print("✅ Restaurant Mock Database Created")

# (Optional) quick sanity check:
cursor.execute("""
SELECT o.order_id, o.order_type, c.name AS customer, s.name AS staff, o.status
FROM restaurant_order o
LEFT JOIN customer c ON c.customer_id = o.customer_id
LEFT JOIN staff s ON s.staff_id = o.staff_id
ORDER BY o.order_id;
""")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
