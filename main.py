import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from master_prompt import MasterPromptGenerator

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

def execute_query(query):
    cursor.execute(query)
    return cursor.fetchall()

def main():
    print("Welcome to the Restaurant Management CLI!")
    print("Type 'exit' to quit.")
    generator = MasterPromptGenerator()
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() == 'exit':
            break
        try:
            prompt = generator.generate_prompt(user_input)
            results = execute_query(prompt)
            for row in results:
                print(row)
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()  # Reset the transaction after an error

if __name__ == "__main__":
    main()


cursor.close()
conn.close()
