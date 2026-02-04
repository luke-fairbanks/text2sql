import os
import init_db
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

schema = init_db.schema_sql

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class MasterPromptGenerator:

    def get_db_schema_create_table(self):
        """Technique: CreateTable (Standard DDL)"""
        return schema.strip()

    def generate_prompt(self, user_query: str) -> str:
        prompt = f"""
        You are an expert SQL generator for a restaurant management system using PostgreSQL with TimescaleDB extension. Using valid SQL syntax, generate a query to answer the user's question based on the provided database schema. Only generate the SQL query without any explanations or comments. Ensure that your SQL query is syntactically correct and can be executed against the given schema.
        Here is the database schema:
        {self.get_db_schema_create_table()}
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

    def generate_sql_query(self, user_query: str) -> str:
        prompt = self.generate_prompt(user_query)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Only output the SQL query, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        sql_query = self.clean_response(response.choices[0].message.content)
        return sql_query
