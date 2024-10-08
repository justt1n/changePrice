import sqlite3
from sqlite3 import Error

class SQLiteDB:
    def __init__(self, db_file):
        """ initialize with the database file """
        self.db_file = db_file
        self.conn = None

    def create_connection(self):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(f"SQLite version {sqlite3.version} connected successfully to {self.db_file}")
        except Error as e:
            print(e)

    def close_connection(self):
        """ close the database connection """
        if self.conn:
            self.conn.close()

    def execute_query(self, query):
        """ Execute a single query """
        if self.conn is None:
            self.create_connection()

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
        except Error as e:
            print(e)

    def fetch_query(self, query):
        """ Execute a query and return the fetched result """
        if self.conn is None:
            self.create_connection()

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(e)