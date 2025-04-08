# server/utils/database_utils.py
from server.database.db_config import get_db_connection, close_connection
import uuid
import os


def create_project_database(project_id, project_number=None):
    """
    Creates a new project-specific database and tables

    Args:
        project_id (str): The UUID of the project
        project_number (str, optional): The project number (not used for DB name anymore)

    Returns:
        bool: True if successful, False otherwise
    """
    # Create database name using project UUID (removing hyphens)
    try:
        # Ensure project_id is a valid UUID string and convert any hyphens
        if isinstance(project_id, bytes):
            # If it's binary, convert to UUID string
            project_id = str(uuid.UUID(bytes=project_id))

        # Create database name using sanitized UUID (removing hyphens)
        clean_uuid = str(project_id).replace('-', '')
        db_name = f"SPACELOGIC_{clean_uuid}"
    except Exception as e:
        print(f"Error formatting UUID for database name: {e}")
        return False

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
                program_number VARCHAR(100) NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                sector VARCHAR(200),
                functional_unit VARCHAR(100),
                level VARCHAR(50),
                planned_area DOUBLE NOT NULL,
                UNIQUE(program_number)
            )
        """)

        cursor.execute("""
            CREATE INDEX idx_rooms_sort ON rooms(functional_unit, sector, name)
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
                user_id BINARY(16) NULL,
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

        cursor.execute("""
            CREATE TABLE interior_fenestration (
                interior_fenestration_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                interior_fenestration_category VARCHAR(100),
                interior_fenestration_number VARCHAR(100),
                interior_fenestration_name VARCHAR(200),
                interior_fenestration_commentary TEXT,
                interior_fenestration_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE exterior_fenestration (
                exterior_fenestration_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                exterior_fenestration_category VARCHAR(100),
                exterior_fenestration_number VARCHAR(100),
                exterior_fenestration_name VARCHAR(200),
                exterior_fenestration_commentary TEXT,
                exterior_fenestration_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE finishes (
                finishes_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                finishes_category VARCHAR(100),
                finishes_number VARCHAR(100),
                finishes_name VARCHAR(200),
                finishes_commentary TEXT,
                finishes_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE doors (
                doors_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                doors_category VARCHAR(100),
                doors_number VARCHAR(100),
                doors_name VARCHAR(200),
                doors_commentary TEXT,
                doors_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE built_in_furniture (
                built_in_furniture_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                built_in_furniture_category VARCHAR(100),
                built_in_furniture_number VARCHAR(100),
                built_in_furniture_name VARCHAR(200),
                built_in_furniture_commentary TEXT,
                built_in_furniture_quantity INT,
                built_in_furniture_date DATE,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE accessories (
                accessories_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                accessories_category VARCHAR(100),
                accessories_number VARCHAR(100),
                accessories_name VARCHAR(200),
                accessories_commentary TEXT,
                accessories_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE plumbings (
                plumbings_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                plumbings_category VARCHAR(100),
                plumbings_number VARCHAR(100),
                plumbings_name VARCHAR(200),
                plumbings_commentary TEXT,
                plumbings_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE fire_protection (
                fire_protection_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                fire_protection_category VARCHAR(100),
                fire_protection_number VARCHAR(100),
                fire_protection_name VARCHAR(200),
                fire_protection_commentary TEXT,
                fire_protection_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE lighting (
                lighting_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                lighting_category VARCHAR(100),
                lighting_number VARCHAR(100),
                lighting_name VARCHAR(200),
                lighting_commentary TEXT,
                lighting_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE electrical_outlets (
                electrical_outlets_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                electrical_outlets_category VARCHAR(100),
                electrical_outlets_number VARCHAR(100),
                electrical_outlets_name VARCHAR(200),
                electrical_outlets_commentary TEXT,
                electrical_outlets_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE communication_security (
                communication_security_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                communication_security_category VARCHAR(100),
                communication_security_number VARCHAR(100),
                communication_security_name VARCHAR(200),
                communication_security_commentary TEXT,
                communication_security_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE medical_equipment (
                medical_equipment_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                medical_equipment_category VARCHAR(100),
                medical_equipment_number VARCHAR(100),
                medical_equipment_name VARCHAR(200),
                medical_equipment_commentary TEXT,
                medical_equipment_quantity INT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE functionality (
		        functionality_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
		        room_id BINARY(16) NOT NULL,
		        functionality_occupants_number INT,
		        functionality_desk_number INT,
		        functionality_lab_number INT,
		        functionality_schedule VARCHAR(100),
		        functionality_access SET('client_access', 'stretcher_access',
		            'bed_access', 'patients_access','exterior_access', 'hallway_access',
		            'adj_room_access', 'other') ,
		        functionality_access_adj_room TEXT,
		        functionality_access_other TEXT,
		        functionality_consideration SET('NA', 'anti_suicide', 'waterproof', 'radiation',
                    'electromagnetic', 'sterile', 'vibrations_sensitivity', 'wet_lab', 'dry_lab',
		            'biosecurity', 'pet_shop' ),
		        functionality_consideration_other TEXT DEFAULT NULL,
		        functionality_description TEXT,
		        functionality_proximity TEXT,
		        functionality_commentary TEXT,
		        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
		    )
        """)

        cursor.execute("""
            CREATE TABLE arch_requirements (
		        arch_requirements_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
		        room_id BINARY(16) NOT NULL,
		        arch_requirements_critic_length INT,
		        arch_requirements_critic_width INT,
		        arch_requirements_critic_height INT,
		        arch_requirements_validation_req INT,
		        arch_requirements_acoustic INT,
		        arch_requirements_int_fenestration SET('not_required', 'with_hallway', 'clear_glass',
                    'frosted_glass', 'semi_frosted_glass', 'one_way_glass', 'integrated_blind'),
		        arch_requirements_int_fen_adj_room TEXT,
		        arch_requirements_int_fen_other TEXT,
		        arch_requirements_ext_fenestration SET('not_required', 'required', 'total_obscurity',
                    'frosted_glass', 'tinted_glass', 'integrated_blind'),
		        arch_requirements_ext_fen_solar_blind TEXT DEFAULT NULL,
		        arch_requirements_ext_fen_opaque_blind TEXT DEFAULT NULL,
		        arch_requirements_commentary TEXT,
		        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
		    )
        """)

        cursor.execute("""
            CREATE TABLE struct_requirements (
		        struct_requirements_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
		        room_id BINARY(16) NOT NULL,
		        struct_requirements_floor_overload_required INT,
		        struct_requirements_overload INT DEFAULT NULL,
		        struct_requirements_equipment_weight INT DEFAULT NULL,
		        struct_requirements_floor_flatness INT,
		        struct_requirements_ditch_gutter INT,
		        struct_requirements_steel_sensitivity INT,
		        struct_requirements_equipment_other TEXT,
		        struct_requirements_vibrations_sensitivity INT,
		        struct_requirements_max_vibrations INT DEFAULT NULL,
		        struct_requirements_commentary TEXT,
		        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
		    )
        """)

        cursor.execute("""
            CREATE TABLE risk_elements (
		        risk_elements_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
		        room_id BINARY(16) NOT NULL,
		        risk_elements_general SET('NA', 'concentrated_acids', 'concentrated_base',
		            'water_air_reactive', 'radioactive'),
		        risk_elements_general_radioactive TEXT DEFAULT NULL,
		        risk_elements_biological SET('NA','biological_products', 'pathogens_humans',
		            'pathogens_animals'),
		        risk_elements_gas SET('NA', 'gas_cylinders', 'important_qty', 'toxic_gas'),
		        risk_elements_gas_qty TEXT,
		        risk_elements_gas_toxic_gas TEXT,
		        risk_elements_liquids SET('NA', 'flammable', 'important_qty', 'cryogenic'),
		        risk_elements_liquids_qty TEXT,
		        risk_elements_liquids_cryogenic TEXT,
		        risk_elements_other SET('NA', 'lasers', 'animals'),
		        risk_elements_chemical_products TEXT,
		        risk_elements_commentary TEXT,
		        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
	        )
        """)

        cursor.execute("""
            CREATE TABLE ventilation_cvac (
                ventilation_cvac_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                ventilation_care_area_type VARCHAR(100),
                ventilation VARCHAR(200),
                ventilation_special_mechanics TEXT,
                ventilation_specific_exhaust TEXT,
                ventilation_commentary TEXT,
                ventilation_relative_room_pressure VARCHAR(50),
                ventilation_pressurization VARCHAR(100),
                ventilation_environmental_parameters TEXT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE electricity (
                electricity_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
                room_id BINARY(16) NOT NULL,
                electricity_care_area_type VARCHAR(100),
                electricity_smoke_fire_detection VARCHAR(100),
                electricity_special_equipment TEXT,
                electricity_lighting_type VARCHAR(100),
                electricity_lighting_level VARCHAR(50),
                electricity_lighting_control VARCHAR(100),
                color_temperature VARCHAR(50),
                electricity_lighting TEXT,
                electricity_commentary TEXT,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)

        connection.commit()

        # Close the current connection and reconnect to the project database
        cursor.close()
        connection.close()
        connection = get_db_connection(db_name)

        if connection:
            # Execute the triggers SQL file
            triggers_file_path = os.path.join(os.path.dirname(__file__), '..', 'database',
                                              'historical_change_triggers.sql')
            success_triggers = execute_sql_file(connection, triggers_file_path)
            if not success_triggers:
                print(f"Warning: Failed to create historical change triggers for {db_name}")

            # Execute the procedures SQL file
            procedures_file_path = os.path.join(os.path.dirname(__file__), '..', 'database',
                                                'historical_procedure.sql')
            success_procedures = execute_sql_file(connection, procedures_file_path)
            if not success_procedures:
                print(f"Warning: Failed to create historical utility procedures for {db_name}")

        print(f"Project database '{db_name}' created successfully")
        return True



    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error creating project database: {e}")
        return False
    finally:
        close_connection(connection, cursor)


def execute_sql_file(connection, file_path):
    """
    Executes SQL statements from a file

    Args:
        connection: An active database connection
        file_path: Path to the SQL file

    Returns:
        bool: True if successful, False otherwise
    """
    cursor = None

    try:
        cursor = connection.cursor()

        # Read the SQL file
        with open(file_path, 'r') as f:
            sql_script = f.read()

        # Fix common comment issues (- to --)
        sql_script = sql_script.replace("\n- ", "\n-- ")

        # Split script on DELIMITER to handle these statements correctly
        sql_parts = sql_script.split('DELIMITER')

        # Execute the first part (before any DELIMITER statement)
        if sql_parts[0].strip():
            statements = [stmt.strip() for stmt in sql_parts[0].split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)

        # For the rest, handle the delimiter changes
        for part in sql_parts[1:]:
            if not part.strip():
                continue

            # Get the delimiter
            delimiter_lines = part.lstrip().split('\n', 1)
            if len(delimiter_lines) < 2:
                continue

            delimiter = delimiter_lines[0].strip()
            rest = delimiter_lines[1]

            # Join the rest and split by the delimiter
            sql_commands = rest.split(delimiter)

            # Execute each command
            for cmd in sql_commands:
                if cmd.strip():
                    try:
                        cursor.execute(cmd)
                    except Exception as cmd_error:
                        print(f"Error executing command: {cmd_error}")
                        print(f"Command: {cmd[:100]}...")  # Print first 100 chars for debugging

        connection.commit()
        return True

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error executing SQL file: {e}")
        return False

    finally:
        if cursor:
            cursor.close()


def set_current_user(connection, user_id):
    """Set the current user for historical change tracking

    Args:
        connection: An active database connection
        user_id: UUID string of the current user
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SET @current_user_id = UUID_TO_BIN(%s)", (user_id,))
    except Exception as e:
        print(f"Error setting current user: {e}")
    finally:
        if cursor:
            cursor.close()