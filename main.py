import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TIMESCALE_SERVICE_URL = os.environ.get("TIMESCALE_SERVICE_URL")
if not TIMESCALE_SERVICE_URL:
    print("Error: TIMESCALE_SERVICE_URL environment variable is not set.")
    exit(1)

conn = psycopg2.connect(dsn=TIMESCALE_SERVICE_URL)
cursor = conn.cursor()

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
