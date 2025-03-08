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
            print(f"Debug - Finding projects for user ID: {user_id}")

            query = """
                SELECT BIN_TO_UUID(p.id) as id, p.numero, p.nom, p.description, 
                p.started_at, p.ended_at, p.status, p.type
                FROM projects p
                JOIN project_user pu ON p.id = pu.project_id
                WHERE pu.user_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            print(f"Debug - Query returned {len(results)} projects")

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
            # Print a more detailed error message
            import traceback
            traceback.print_exc()
        finally:
            close_connection(connection, cursor)

        return projects

    @staticmethod
    def count_user_projects(user_id):
        """Count how many projects a user has (for debugging)"""
        connection = get_db_connection()
        cursor = None
        count = 0

        try:
            cursor = connection.cursor()
            query = """
                SELECT COUNT(*) 
                FROM project_user 
                WHERE user_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                count = result[0]
        except Exception as e:
            print(f"Error counting projects: {e}")
        finally:
            close_connection(connection, cursor)

        return count

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

class Organisation:
    def __init__(self, id=None, nom=None, created_at=None, super_admin_id=None):
        self.id = id
        self.nom = nom
        self.created_at = created_at
        self.super_admin_id = super_admin_id

    @staticmethod
    def find_by_id(organisation_id):
        """Find an organisation by ID"""
        connection = get_db_connection()
        cursor = None
        organisation = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, nom, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organisations WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (organisation_id,))
            result = cursor.fetchone()

            if result:
                organisation = Organisation(
                    id=result['id'],
                    nom=result['nom'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
        except Exception as e:
            print(f"Error finding organisation by ID: {e}")
        finally:
            close_connection(connection, cursor)

        return organisation

    @staticmethod
    def find_by_name(nom):
        """Find an organisation by name"""
        connection = get_db_connection()
        cursor = None
        organisation = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, nom, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organisations WHERE nom = %s
            """
            cursor.execute(query, (nom,))
            result = cursor.fetchone()

            if result:
                organisation = Organisation(
                    id=result['id'],
                    nom=result['nom'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
        except Exception as e:
            print(f"Error finding organisation by name: {e}")
        finally:
            close_connection(connection, cursor)

        return organisation

    @staticmethod
    def find_all():
        """Find all organisations"""
        connection = get_db_connection()
        cursor = None
        organisations = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, nom, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organisations
            """
            cursor.execute(query)
            results = cursor.fetchall()

            for result in results:
                organisation = Organisation(
                    id=result['id'],
                    nom=result['nom'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
                organisations.append(organisation)
        except Exception as e:
            print(f"Error finding all organisations: {e}")
        finally:
            close_connection(connection, cursor)

        return organisations

    @staticmethod
    def find_by_user(user_id):
        """Find all organisations for a user"""
        connection = get_db_connection()
        cursor = None
        organisations = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(o.id) as id, o.nom, o.created_at, 
                BIN_TO_UUID(o.super_admin_id) as super_admin_id
                FROM organisations o
                JOIN organisation_user ou ON o.id = ou.organisations_id
                WHERE ou.users_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()

            for result in results:
                organisation = Organisation(
                    id=result['id'],
                    nom=result['nom'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
                organisations.append(organisation)
        except Exception as e:
            print(f"Error finding organisations for user: {e}")
        finally:
            close_connection(connection, cursor)

        return organisations

    def save(self):
        """Save organisation to database"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()

            if self.id:  # Update existing organisation
                query = """
                    UPDATE organisations
                    SET nom = %s, super_admin_id = NULLIF(UUID_TO_BIN(%s), UUID_TO_BIN(NULL))
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (self.nom, self.super_admin_id, self.id)
            else:  # Create new organisation
                query = """
                    INSERT INTO organisations (nom, super_admin_id)
                    VALUES (%s, NULLIF(UUID_TO_BIN(%s), UUID_TO_BIN(NULL)))
                """
                values = (self.nom, self.super_admin_id)

            # Execute with the parameter that suppresses result sets
            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new organisation
            if not self.id:
                # Use a new cursor to avoid any previous result issues
                cursor.close()
                cursor = connection.cursor()
                cursor.execute("SELECT LAST_INSERT_ID()")
                last_id = cursor.fetchone()

                if last_id and last_id[0]:
                    # Convert binary ID back to string UUID
                    cursor.close()
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT BIN_TO_UUID(id) FROM organisations WHERE id = LAST_INSERT_ID()")
                    uuid_result = cursor.fetchone()
                    if uuid_result:
                        self.id = uuid_result[0]

            return True
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error saving organisation: {e}")
            return False
        finally:
            if cursor:
                try:
                    # Try to consume any remaining results
                    while cursor.nextset():
                        pass
                except:
                    pass
            close_connection(connection, cursor)

    def add_user(self, user_id):
        """Add a user to the organisation"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO organisation_user (organisations_id, users_id)
                VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))
            """
            cursor.execute(query, (self.id, user_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error adding user to organisation: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def remove_user(self, user_id):
        """Remove a user from the organisation"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                DELETE FROM organisation_user
                WHERE organisations_id = UUID_TO_BIN(%s) AND users_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id, user_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error removing user from organisation: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def get_users(self):
        """Get all users in the organisation"""
        connection = get_db_connection()
        cursor = None
        users = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(u.id) as id, u.nom, u.prenom, u.email, 
                u.created_at, u.is_active
                FROM users u
                JOIN organisation_user ou ON u.id = ou.users_id
                WHERE ou.organisations_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            for result in results:
                from server.models.user import User  # Import here to avoid circular imports
                user = User(
                    id=result['id'],
                    nom=result['nom'],
                    prenom=result['prenom'],
                    email=result['email'],
                    created_at=result['created_at'],
                    is_active=result['is_active']
                )
                users.append(user)
        except Exception as e:
            print(f"Error getting users for organisation: {e}")
        finally:
            close_connection(connection, cursor)

        return users

    def get_projects(self):
        """Get all projects in the organisation"""
        connection = get_db_connection()
        cursor = None
        projects = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, numero, nom, description, 
                started_at, ended_at, status, type
                FROM projects 
                WHERE org_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            for result in results:
                from server.models.project import Project  # Import here to avoid circular imports
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
            print(f"Error getting projects for organisation: {e}")
        finally:
            close_connection(connection, cursor)

        return projects

    def add_role(self, role_name, role_description=None):
        """Add a role to the organisation"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO organisationRoles (organisation_id, nom, description)
                VALUES (UUID_TO_BIN(%s), %s, %s)
            """
            cursor.execute(query, (self.id, role_name, role_description))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error adding role to organisation: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def get_roles(self):
        """Get all roles in the organisation"""
        connection = get_db_connection()
        cursor = None
        roles = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, nom, description, created_at
                FROM organisationRoles
                WHERE organisation_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            for result in results:
                role = {
                    'id': result['id'],
                    'nom': result['nom'],
                    'description': result['description'],
                    'created_at': result['created_at']
                }
                roles.append(role)
        except Exception as e:
            print(f"Error getting roles for organisation: {e}")
        finally:
            close_connection(connection, cursor)

        return roles

    def assign_role_to_user(self, user_id, role_id):
        """Assign a role to a user in the organisation"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO user_organisation_role (user_id, organisation_id, role_id)
                VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s), UUID_TO_BIN(%s))
            """
            cursor.execute(query, (user_id, self.id, role_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error assigning role to user: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def get_user_roles(self, user_id):
        """Get all roles for a user in the organisation"""
        connection = get_db_connection()
        cursor = None
        roles = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(r.id) as id, r.nom, r.description, r.created_at
                FROM organisationRoles r
                JOIN user_organisation_role uor ON r.id = uor.role_id
                WHERE uor.user_id = UUID_TO_BIN(%s) AND uor.organisation_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id, self.id))
            results = cursor.fetchall()

            for result in results:
                role = {
                    'id': result['id'],
                    'nom': result['nom'],
                    'description': result['description'],
                    'created_at': result['created_at']
                }
                roles.append(role)
        except Exception as e:
            print(f"Error getting roles for user in organisation: {e}")
        finally:
            close_connection(connection, cursor)

        return roles

    def delete(self):
        """Delete the organisation"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                DELETE FROM organisations
                WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error deleting organisation: {e}")
            return False
        finally:
            close_connection(connection, cursor)