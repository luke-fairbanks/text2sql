import os
import table
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

schema = table.schema_sql

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class MasterPromptGenerator:

    def get_db_schema_create_table(self):
        """Technique: CreateTable (Standard DDL)"""
        return schema.strip()

    def get_db_content_select_col(self, cursor):
        """Technique: SelectCol (Distinct Examples)"""
        prompt_lines = []

        # PostgreSQL: Get all public tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]

        for t in table_names:
            prompt_lines.append(f"/*\nColumns in {t} and 3 distinct examples in each column:")

            # PostgreSQL: Get columns for table
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='{t}'")
            col_info = cursor.fetchall()
            col_names = [c[0] for c in col_info]

            for col in col_names:
                try:
                    # PostgreSQL: Quote identifiers to be safe
                    cursor.execute(f'SELECT DISTINCT "{col}" FROM "{t}" LIMIT 3')
                    rows = cursor.fetchall()
                    vals = []
                    for r in rows:
                        val = r[0]
                        if isinstance(val, str):
                            vals.append(f"'{val}'")
                        else:
                            vals.append(str(val))
                    if vals:
                        prompt_lines.append(f"{col}: {', '.join(vals)}")
                except:
                    continue
            prompt_lines.append("*/")
        return "\n".join(prompt_lines)

    def generate_prompt(self, user_query: str, cursor) -> str:
        prompt = f"""
        You are an expert SQL generator for a restaurant management system using PostgreSQL with TimescaleDB extension. Using valid SQL syntax, generate a query to answer the user's question based on the provided database schema. Only generate the SQL query without any explanations or comments. Ensure that your SQL query is syntactically correct and can be executed against the given schema.
        Here is the database schema:
        {self.get_db_schema_create_table()}
        Here is the database content for context:
        {self.get_db_content_select_col(cursor)}
        Generate a SQL query to answer the following question:
        {user_query}
        """
        return prompt.strip()

    def clean_response(self, response: str) -> str:
        """Cleans the model's response to extract only the SQL query."""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```sql"):
            response = response[6:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return response.strip()

    def generate_sql_query(self, user_query: str, cursor) -> str:
        prompt = self.generate_prompt(user_query, cursor)
        # print("Generated Prompt for LLM:")
        # print(prompt)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Only output the SQL query, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        sql_query = self.clean_response(response.choices[0].message.content)
        return sql_query

    def generate_friendly_report(self, user_query: str, sql_query: str, sql_results: list) -> str:
        """Generate a user-friendly report from SQL query results."""
        prompt = f"""
        You are a helpful assistant for a restaurant management system. A user asked a question, and a SQL query was executed to get the answer.

        User's original question: {user_query}

        SQL query that was executed: {sql_query}

        Query results: {sql_results}

        Please provide a clear, friendly, and well-formatted response that answers the user's question based on these results.
        - If the results are empty, let the user know no data was found.
        - Format numbers nicely (e.g., currency with $ signs where appropriate).
        - Summarize the data in a natural, conversational way.
        - Keep the response concise but informative.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a friendly assistant that explains database query results in a clear, conversational manner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

masterprompt = MasterPromptGenerator()
# print(MasterPromptGenerator.get_db_schema_create_table(masterprompt))