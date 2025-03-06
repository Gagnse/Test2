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