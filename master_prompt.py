import init_db

schema = init_db.schema_sql



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
        return response.strip()
