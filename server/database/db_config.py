import os
import mysql.connector
from mysql.connector import Error

# Database connection configuration

DB_CONFIG = {
    'users_db': {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'spacelogic'),
        'password': os.environ.get('DB_PASSWORD', 'glo2005'),
        'database': os.environ.get('DB_USERS_NAME', 'SPACELOGIC_ADMIN_DB'),
        'port': int(os.environ.get('DB_PORT', 3306))
    },
    'project_db': {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'spacelogic'),
        'password': os.environ.get('DB_PASSWORD', 'glo2005'),
        'database': os.environ.get('DB_PROJECT_NAME', 'SPACELOGIC_projet1'),
        'port': int(os.environ.get('DB_PORT', 3306))
    }
}


def get_db_connection(db_name='users_db'):
    """
    Create and return a database connection for the specified database.

    :param db_name: The key of the database in DB_CONFIG ('users_db' or 'project_db')
    :return: MySQL connection object or None if connection fails.
    """
    if db_name not in DB_CONFIG:
        print(f"Error: Database '{db_name}' is not defined in DB_CONFIG.")
        return None

    try:
        config = DB_CONFIG[db_name]  # Récupère les infos de connexion pour la DB choisie
        print(f"Attempting to connect to MySQL database: {config['database']} on {config['host']}:{config['port']}")

        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            port=config['port']
        )

        if connection.is_connected():
            print(f"Successfully connected to MySQL database '{config['database']}'!")
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
    Close database connection and cursor if provided.
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
        print("Database connection closed.")