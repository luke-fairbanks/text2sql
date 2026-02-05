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
            sql_query = generator.generate_sql_query(user_input, cursor)
            print(f"Generated SQL: {sql_query}")
            sql_results = execute_query(sql_query)
            report = generator.generate_friendly_report(user_input, sql_query, sql_results)
            print("\n" + "="*50)
            print(report)
            print("="*50 + "\n")
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()

if __name__ == "__main__":
    main()


cursor.close()
conn.close()
