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


class Organisation:
    def __init__(self, id=None, nom=None, created_at=None, super_admin_id=None):
        self.id = id
        self.nom = nom
        self.created_at = created_at
        self.super_admin_id = super_admin_id

    @staticmethod
    def find_by_id(org_id):
        """Find an organization by ID"""
        connection = get_db_connection()
        cursor = None
        org = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, nom, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organisations WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (org_id,))
            result = cursor.fetchone()

            if result:
                org = Organisation(
                    id=result['id'],
                    nom=result['nom'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
        except Exception as e:
            print(f"Error finding organization by ID: {e}")
        finally:
            close_connection(connection, cursor)

        return org

    @staticmethod
    def find_by_user(user_id):
        """Find all organizations for a user"""
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
                UNION
                SELECT BIN_TO_UUID(o.id) as id, o.nom, o.created_at, 
                BIN_TO_UUID(o.super_admin_id) as super_admin_id
                FROM organisations o
                WHERE o.super_admin_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id, user_id))
            results = cursor.fetchall()

            for result in results:
                org = Organisation(
                    id=result['id'],
                    nom=result['nom'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
                organisations.append(org)
        except Exception as e:
            print(f"Error finding organizations for user: {e}")
        finally:
            close_connection(connection, cursor)

        return organisations

    @staticmethod
    def check_user_role(org_id, user_id, role_name):
        """Check if a user has a specific role in the organization"""
        connection = get_db_connection()
        cursor = None
        has_role = False

        try:
            cursor = connection.cursor()
            query = """
                SELECT COUNT(*) FROM user_organisation_role uor
                JOIN organisationRoles r ON uor.role_id = r.id
                WHERE uor.organisation_id = UUID_TO_BIN(%s)
                AND uor.user_id = UUID_TO_BIN(%s)
                AND r.nom = %s
            """
            cursor.execute(query, (org_id, user_id, role_name))
            result = cursor.fetchone()

            if result and result[0] > 0:
                has_role = True
        except Exception as e:
            print(f"Error checking user role: {e}")
        finally:
            close_connection(connection, cursor)

        return has_role

    @staticmethod
    def get_users_with_roles(org_id):
        """Get all users in an organization with their roles"""
        connection = get_db_connection()
        cursor = None
        users = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(u.id) as id, u.nom, u.prenom, u.email, 
                       u.company, u.department, u.location, u.created_at,
                       BIN_TO_UUID(r.id) as role_id, r.nom as role_name,
                       o.super_admin_id = u.id as is_super_admin
                FROM users u
                JOIN organisation_user ou ON u.id = ou.users_id
                LEFT JOIN user_organisation_role uor ON u.id = uor.user_id AND uor.organisation_id = UUID_TO_BIN(%s)
                LEFT JOIN organisationRoles r ON uor.role_id = r.id
                JOIN organisations o ON o.id = UUID_TO_BIN(%s)
                WHERE ou.organisations_id = UUID_TO_BIN(%s)

                UNION

                SELECT BIN_TO_UUID(u.id) as id, u.nom, u.prenom, u.email, 
                       u.company, u.department, u.location, u.created_at,
                       NULL as role_id, 'Super Admin' as role_name,
                       1 as is_super_admin
                FROM users u
                JOIN organisations o ON o.super_admin_id = u.id
                WHERE o.id = UUID_TO_BIN(%s)
                AND u.id NOT IN (
                    SELECT users_id FROM organisation_user 
                    WHERE organisations_id = UUID_TO_BIN(%s)
                )
            """
            cursor.execute(query, (org_id, org_id, org_id, org_id, org_id))
            results = cursor.fetchall()

            users = results
        except Exception as e:
            print(f"Error getting users with roles: {e}")
        finally:
            close_connection(connection, cursor)

        return users

    @staticmethod
    def get_available_roles(org_id):
        """Get all available roles for an organization"""
        connection = get_db_connection()
        cursor = None
        roles = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, nom, description
                FROM organisationRoles
                WHERE organisation_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (org_id,))
            roles = cursor.fetchall()
        except Exception as e:
            print(f"Error getting available roles: {e}")
        finally:
            close_connection(connection, cursor)

        return roles

    @staticmethod
    def update_user_info(org_id, user_id, role_id, company, location):
        """Update a user's role and info in an organization"""
        connection = get_db_connection()
        cursor = None
        success = False

        try:
            cursor = connection.cursor()

            # Start a transaction
            connection.start_transaction()

            # Update the user's company and location
            user_query = """
                UPDATE users
                SET company = %s, location = %s
                WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(user_query, (company, location, user_id))

            # Check if the user already has a role in this organization
            role_check_query = """
                SELECT COUNT(*) FROM user_organisation_role
                WHERE user_id = UUID_TO_BIN(%s)
                AND organisation_id = UUID_TO_BIN(%s)
            """
            cursor.execute(role_check_query, (user_id, org_id))
            has_role = cursor.fetchone()[0] > 0

            if role_id:
                if has_role:
                    # Update the existing role
                    role_update_query = """
                        UPDATE user_organisation_role
                        SET role_id = UUID_TO_BIN(%s)
                        WHERE user_id = UUID_TO_BIN(%s)
                        AND organisation_id = UUID_TO_BIN(%s)
                    """
                    cursor.execute(role_update_query, (role_id, user_id, org_id))
                else:
                    # Insert a new role
                    role_insert_query = """
                        INSERT INTO user_organisation_role (user_id, organisation_id, role_id)
                        VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s), UUID_TO_BIN(%s))
                    """
                    cursor.execute(role_insert_query, (user_id, org_id, role_id))
            elif has_role:
                # Remove the role
                role_delete_query = """
                    DELETE FROM user_organisation_role
                    WHERE user_id = UUID_TO_BIN(%s)
                    AND organisation_id = UUID_TO_BIN(%s)
                """
                cursor.execute(role_delete_query, (user_id, org_id))

            # Commit the transaction
            connection.commit()
            success = True
        except Exception as e:
            # Rollback in case of error
            connection.rollback()
            print(f"Error updating user info: {e}")
        finally:
            close_connection(connection, cursor)

        return success

    def save(self):
        """Save organization to database"""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()

            if self.id:  # Update existing organization
                query = """
                    UPDATE organisations
                    SET nom = %s, super_admin_id = UUID_TO_BIN(%s)
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (self.nom, self.super_admin_id, self.id)
            else:  # Create new organization
                query = """
                    INSERT INTO organisations (nom, super_admin_id)
                    VALUES (%s, UUID_TO_BIN(%s))
                """
                values = (self.nom, self.super_admin_id)

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new organization
            if not self.id:
                query = "SELECT BIN_TO_UUID(LAST_INSERT_ID()) as id"
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    self.id = result[0]

            return True
        except Exception as e:
            connection.rollback()
            print(f"Error saving organization: {e}")
            return False
        finally:
            close_connection(connection, cursor)