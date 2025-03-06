import uuid
import bcrypt
from server.database.db_config import get_db_connection, close_connection


class User:
    def __init__(self, id=None, nom=None, prenom=None, email=None, password=None, created_at=None, is_active=True):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.password = password
        self.created_at = created_at
        self.is_active = is_active

    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        connection = get_db_connection()
        cursor = None
        user = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT BIN_TO_UUID(id) as id, nom, prenom, email, password, created_at, is_active FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            if result:
                user = User(
                    id=result['id'],
                    nom=result['nom'],
                    prenom=result['prenom'],
                    email=result['email'],
                    password=result['password'],
                    created_at=result['created_at'],
                    is_active=result['is_active']
                )
        except Exception as e:
            print(f"Error finding user by email: {e}")
        finally:
            close_connection(connection, cursor)

        return user

    def save(self):
        """Save user to database"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()

            # Hash the password if it's not already hashed
            if not self.password.startswith('$2b$'):
                self.password = self.hash_password(self.password)

            # Use MySQL's UUID_TO_BIN function to convert UUID to binary
            query = """
                INSERT INTO users (nom, prenom, email, password)
                VALUES (%s, %s, %s, %s)
            """
            values = (self.nom, self.prenom, self.email, self.password)

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID
            self.id = cursor.lastrowid
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error saving user: {e}")
            return False
        finally:
            close_connection(connection, cursor)


class Project:
    def __init__(self, id=None, numero=None, nom=None, description=None,
                 started_at=None, ended_at=None, status=None, type=None):
        self.id = id
        self.numero = numero
        self.nom = nom
        self.description = description
        self.started_at = started_at
        self.ended_at = ended_at
        self.status = status
        self.type = type

    @staticmethod
    def find_by_id(project_id):
        """Find a project by ID"""
        connection = get_db_connection()
        cursor = None
        project = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT BIN_TO_UUID(id) as id, numero, nom, description, " \
                    "started_at, ended_at, status, type FROM projects WHERE id = UUID_TO_BIN(%s)"
            cursor.execute(query, (project_id,))
            result = cursor.fetchone()

            if result:
                project = Project(
                    id=result['id'],
                    numero=result['numero'],
                    nom=result['nom'],
                    description=result['description'],
                    started_at=result['started_at'],
                    ended_at=result['ended_at'],
                    status=result['status'],
                    type=result['type']
                )
        except Exception as e:
            print(f"Error finding project by ID: {e}")
        finally:
            close_connection(connection, cursor)

        return project

    @staticmethod
    def find_by_user(user_id):
        """Find all projects for a user"""
        connection = get_db_connection()
        cursor = None
        projects = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(p.id) as id, p.numero, p.nom, p.description, 
                p.started_at, p.ended_at, p.status, p.type
                FROM projects p
                JOIN project_user pu ON p.id = pu.project_id
                WHERE pu.user_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()

            for result in results:
                project = Project(
                    id=result['id'],
                    numero=result['numero'],
                    nom=result['nom'],
                    description=result['description'],
                    started_at=result['started_at'],
                    ended_at=result['ended_at'],
                    status=result['status'],
                    type=result['type']
                )
                projects.append(project)
        except Exception as e:
            print(f"Error finding projects for user: {e}")
        finally:
            close_connection(connection, cursor)

        return projects

    def save(self):
        """Save project to database"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()

            if self.id:  # Update existing project
                query = """
                    UPDATE projects
                    SET numero = %s, nom = %s, description = %s, started_at = %s, 
                    ended_at = %s, status = %s, type = %s
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (
                    self.numero, self.nom, self.description,
                    self.started_at, self.ended_at, self.status, self.type, self.id
                )
            else:  # Create new project
                query = """
                    INSERT INTO projects (numero, nom, description, started_at, ended_at, status, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    self.numero, self.nom, self.description,
                    self.started_at, self.ended_at, self.status, self.type
                )

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new project
            if not self.id:
                self.id = cursor.lastrowid

            return True
        except Exception as e:
            connection.rollback()
            print(f"Error saving project: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def add_user(self, user_id):
        """Add a user to the project"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO project_user (project_id, user_id)
                VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))
            """
            cursor.execute(query, (self.id, user_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error adding user to project: {e}")
            return False
        finally:
            close_connection(connection, cursor)