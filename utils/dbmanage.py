from sys import path
import os
project_root = os.path.dirname(os.path.realpath(__file__))
path.append(os.path.join(project_root, '..'))

import pyodbc
from utils.config import read_config

class MSSQLManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def dbconnect(self):
        self.config = read_config()
        host = self.config.get('mssql', 'host')
        port = self.config.get('mssql', 'port')
        db = self.config.get('mssql', 'db')
        username = self.config.get('mssql', 'username')
        password = self.config.get('mssql', 'password')
        CONNECTION_STRING = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};UID={username};DATABASE={db};PWD={password};'
        try:
            self.connection = pyodbc.connect(CONNECTION_STRING)
            self.cursor = self.connection.cursor()
            print("Connected to the database successfully...")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def get_connection(self):
        return self.connection

    def get_cursor(self):
        return self.cursor

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully...")
        except Exception as e:
            print(f"Error executing query: {e}")

    def fetch_data(self, query):
        try:
            result = self.cursor.execute(query).fetchall()
            return result
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def close_connection(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")

# Example usage:
mssql_manager = MSSQLManager()

# Get connection and cursor
connection = mssql_manager.get_connection()
cursor = mssql_manager.get_cursor()

# Example: Execute a query
create_table_query = """
SELECT * from ExternalUser.MES_DEV.MES_SCHEDULED_INSTALL_TRACKER
where LOAD_DATE ='2023-12-12' AND 
RESOLUTION like '%Successful%'"""
mssql_manager.execute_query(create_table_query)

# Close the connection
mssql_manager.close_connection()
