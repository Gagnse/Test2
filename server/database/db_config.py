import os
import mysql.connector
from mysql.connector import Error

# Database connection configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'SPACELOGIC'),
    'port': os.environ.get('DB_PORT', 3306)
}


def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        print(
            f"Attempting to connect to MySQL database: {DB_CONFIG['database']} on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL database!")
            return connection
        else:
            print("Connection object created but not connected")
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    except Exception as e:
        print(f"Unexpected error connecting to MySQL: {e}")

    print("Failed to establish database connection. Check your MySQL settings and ensure the server is running.")
    return None


def close_connection(connection, cursor=None):
    """
    Close database connection and cursor if provided
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()