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
    Vérifie si une base de données existe dans MySQL.
    """
    print(f"🔍 Vérification de l'existence de la base : {database_name}")

    # Se connecter à MySQL sans spécifier de base pour pouvoir lister toutes les bases
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
    Crée une connexion MySQL pour une base de données spécifique.

    :param db_name: Nom de la base de données (ex: 'users_db' ou 'SPACELOGIC_<numéro_projet>')
    :return: Objet de connexion MySQL ou None si la connexion échoue.
    """
    if db_name == 'users_db':
        # 🔹 Connexion à la base admin (SPACELOGIC_ADMIN_DB)
        config = DB_CONFIG['users_db']
    elif db_name.startswith("SPACELOGIC_"):
        # 🔹 Connexion dynamique à une base projet (SPACELOGIC_<numéro_projet>)
        config = DB_CONFIG['users_db'].copy()  # Utilise les mêmes credentials que users_db
        config['database'] = db_name  # Définit la base spécifique au projet
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

    # def get_db_connection(db_name='users_db'):
    #     """
    #     Create and return a database connection for the specified database.
    #
    #     :param db_name: The key of the database in DB_CONFIG ('users_db' or 'project_db')
    #     :return: MySQL connection object or None if connection fails.
    #     """
    #     if db_name not in DB_CONFIG:
    #         print(f"Error: Database '{db_name}' is not defined in DB_CONFIG.")
    #         return None
    #
    #     try:
    #         config = DB_CONFIG[db_name]  # Récupère les infos de connexion pour la DB choisie
    #         print(f"Attempting to connect to MySQL database: {config['database']} on {config['host']}:{config['port']}")
    #
    #         connection = mysql.connector.connect(
    #             host=config['host'],
    #             user=config['user'],
    #             password=config['password'],
    #             database=config['database'],
    #             port=config['port']
    #         )
    #
    #         if connection.is_connected():
    #             print(f"Successfully connected to MySQL database '{config['database']}'!")
    #             return connection
    #         else:
    #             print("Connection object created but not connected")
    #     except Error as e:
    #         print(f"Error connecting to MySQL: {e}")
    #     except Exception as e:
    #         print(f"Unexpected error connecting to MySQL: {e}")
    #
    #     print("Failed to establish database connection. Check your MySQL settings and ensure the server is running.")
    #     return None



