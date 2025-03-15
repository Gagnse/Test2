# server/utils/database_utils.py
from server.database.db_config import get_db_connection, close_connection

def create_project_database(project_id, project_number):
    """
    Creates a new project-specific database and tables

    Args:
        project_id (str): The UUID of the project
        project_number (str): The project number to use in the database name

    Returns:
        bool: True if successful, False otherwise
    """
    # Sanitize project number for database name
    db_name = f"SPACELOGIC_{project_number.replace('-', '_')}"

    # Get a connection to the database
    connection = get_db_connection('users_db')
    cursor = None

    try:
        cursor = connection.cursor()

        # Create the new database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")

        # Switch to the new database
        cursor.execute(f"USE {db_name}")

        # Create project-specific tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                program_number VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                sector VARCHAR(50),
                functional_unit VARCHAR(50),
                level VARCHAR(50),
                planned_area DOUBLE NOT NULL,
                UNIQUE(program_number)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disciplines (
                id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                UNIQUE(name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_disciplines (
                room_id BINARY(16) NOT NULL,
                discipline_id BINARY(16) NOT NULL,
                PRIMARY KEY (room_id, discipline_id),
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_changes (
                id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                entity_id BINARY(16) NOT NULL,
                change_type VARCHAR(50) NOT NULL,
                old_value TEXT,
                new_value TEXT,
                change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                version_number VARCHAR(25) NOT NULL
            )
        """)

        # Create table to store project ID reference
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_reference (
                admin_project_id BINARY(16) NOT NULL,
                PRIMARY KEY (admin_project_id)
            )
        """)

        # Insert the project ID reference
        cursor.execute(
            "INSERT INTO project_reference (admin_project_id) VALUES (UUID_TO_BIN(%s))",
            (project_id,)
        )

        connection.commit()
        print(f"Project database '{db_name}' created successfully")
        return True

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error creating project database: {e}")
        return False
    finally:
        close_connection(connection, cursor)