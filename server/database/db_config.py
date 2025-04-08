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
    }
}

def close_connection(connection, cursor=None):
    """
    Close database connection and cursor if provided.
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
        print("Database connection closed.")


def database_exists(database_name):
    """
    Verify if the database exists.
    """

    # Connection to MySQL to find all the databases
    connection = mysql.connector.connect(
        host=DB_CONFIG['users_db']['host'],
        user=DB_CONFIG['users_db']['user'],
        password=DB_CONFIG['users_db']['password'],
        port=DB_CONFIG['users_db']['port']
    )

    if not connection:
        print(f"❌ Impossible de se connecter à MySQL pour vérifier {database_name}")
        return False

    cursor = connection.cursor()
    cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
    exists = cursor.fetchone() is not None

    cursor.close()
    connection.close()

    print(f"✅ La base {database_name} existe : {exists}")
    return exists

def get_db_connection(db_name='users_db'):
    """
    Create a database connection and return it.

    :param db_name: database name (ex: 'users_db' or 'SPACELOGIC_<project_id>')
    :return: MySQL connection or None if not found.
    """
    if db_name == 'users_db':
        # Connection to admin database (SPACELOGIC_ADMIN_DB)
        config = DB_CONFIG['users_db']
    elif db_name.startswith("SPACELOGIC_"):
        # Connection to a specific project database (SPACELOGIC_<project_id>)
        config = DB_CONFIG['users_db'].copy()  # Same info as users_db
        config['database'] = db_name  # find database specific to a project
    else:
        print(f"❌ Erreur : Base inconnue '{db_name}'")
        return None

    try:
        print(f"🔄 Tentative de connexion à MySQL: {config['database']} sur {config['host']}:{config['port']}")
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            print(f"✅ Connecté à la base de données '{config['database']}'")
            return connection

    except mysql.connector.Error as err:
        print(f"❌ Erreur de connexion à '{config['database']}': {err}")
        return None



