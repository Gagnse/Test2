import uuid
import bcrypt
from server.database.db_config import get_db_connection, close_connection


class User:
    def __init__(self, id=None, first_name=None, last_name=None, email=None, password=None, created_at=None,
                 is_active=True, organization_id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.created_at = created_at
        self.is_active = is_active
        self.organization_id = organization_id

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
        connection = get_db_connection('users_db')
        cursor = None
        user = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, first_name, last_name, 
                email, password, created_at, is_active, 
                BIN_TO_UUID(organization_id) as organization_id 
                FROM users WHERE email = %s
            """
            cursor.execute(query, (email,))
            result = cursor.fetchone()

            if result:
                user = User(
                    id=result['id'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    email=result['email'],
                    password=result['password'],
                    created_at=result['created_at'],
                    is_active=result['is_active'],
                    organization_id=result['organization_id']
                )
        except Exception as e:
            print(f"Error finding user by email: {e}")
        finally:
            close_connection(connection, cursor)

        return user

    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID"""
        connection = get_db_connection('users_db')
        cursor = None
        user = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, first_name, last_name, 
                email, password, created_at, is_active, 
                BIN_TO_UUID(organization_id) as organization_id 
                FROM users WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result:
                user = User(
                    id=result['id'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    email=result['email'],
                    password=result['password'],
                    created_at=result['created_at'],
                    is_active=result['is_active'],
                    organization_id=result['organization_id']
                )
        except Exception as e:
            print(f"Error finding user by ID: {e}")
        finally:
            close_connection(connection, cursor)

        return user

    def save(self):
        """Save user to database"""
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()

            # Get an organization to associate with the user
            # For simplicity, we'll use the first organization in the database
            org_id = None
            try:
                cursor.execute("SELECT BIN_TO_UUID(id) FROM organizations LIMIT 1")
                org_result = cursor.fetchone()
                if org_result:
                    org_id = org_result[0]
            except Exception as e:
                print(f"Error getting default organization: {e}")

            if not org_id:
                print("No organization found for user. Creating a default one.")
                # Create a default organization if none exists
                cursor.execute("INSERT INTO organizations (name) VALUES ('Default Organization')")
                connection.commit()
                cursor.execute("SELECT BIN_TO_UUID(id) FROM organizations WHERE name = 'Default Organization'")
                org_result = cursor.fetchone()
                if org_result:
                    org_id = org_result[0]

            # Hash the password if it's not already hashed
            if not self.password.startswith('$2b$'):
                self.password = self.hash_password(self.password)

            # Use MySQL's UUID_TO_BIN function to convert UUID to binary
            if self.id:  # Update existing user
                query = """
                    UPDATE users 
                    SET first_name = %s, last_name = %s, email = %s, password = %s
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (self.first_name, self.last_name, self.email, self.password, self.id)
            else:  # Create new user
                query = """
                    INSERT INTO users (first_name, last_name, email, password, organization_id)
                    VALUES (%s, %s, %s, %s, UUID_TO_BIN(%s))
                """
                values = (self.first_name, self.last_name, self.email, self.password, org_id)

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for new user
            if not self.id:
                cursor.execute("SELECT BIN_TO_UUID(id) FROM users WHERE email = %s", (self.email,))
                result = cursor.fetchone()
                if result:
                    self.id = result[0]

                    # Add user to the organization
                    if org_id:
                        try:
                            cursor.execute(
                                "INSERT INTO organization_user (organizations_id, users_id) VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))",
                                (org_id, self.id)
                            )
                            connection.commit()
                        except Exception as e:
                            print(f"Error adding user to organization: {e}")

            return True
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error saving user: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def get_user_org_id(user_id):
        """Get a user's organization ID"""
        connection = get_db_connection('users_db')
        cursor = None
        organization_id = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT BIN_TO_UUID(organization_id) as organization_id FROM users WHERE id = UUID_TO_BIN(%s)"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                organization_id = result['organization_id']
        except Exception as e:
            print(f"Error getting user's organization: {e}")
        finally:
            close_connection(connection, cursor)

        return organization_id

class Project:
    def __init__(self, id=None, project_number=None, name=None, description=None,
                 start_date=None, end_date=None, status=None, type=None, organization_id=None):
        self.id = id
        self.project_number = project_number
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.type = type
        self.organization_id = organization_id

    @staticmethod
    def find_by_id(project_id):
        """Find a project by ID"""
        connection = get_db_connection('users_db')
        cursor = None
        project = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, project_number, name, description, 
                start_date, end_date, status, type, BIN_TO_UUID(organization_id) as organization_id 
                FROM projects WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (project_id,))
            result = cursor.fetchone()

            if result:
                project = Project(
                    id=result['id'],
                    project_number=result['project_number'],
                    name=result['name'],
                    description=result['description'],
                    start_date=result['start_date'],
                    end_date=result['end_date'],
                    status=result['status'],
                    type=result['type'],
                    organization_id=result['organization_id']
                )
        except Exception as e:
            print(f"Error finding project by ID: {e}")
        finally:
            close_connection(connection, cursor)

        return project

    @staticmethod
    def find_by_user(user_id):
        """Find all projects for a user"""
        connection = get_db_connection('users_db')
        cursor = None
        projects = []

        try:
            cursor = connection.cursor(dictionary=True)
            print(f"Debug - Finding projects for user ID: {user_id}")

            query = """
                SELECT BIN_TO_UUID(p.id) as id, p.project_number, p.name, p.description, 
                p.start_date, p.end_date, p.status, p.type, BIN_TO_UUID(p.organization_id) as organization_id
                FROM projects p
                JOIN project_users pu ON p.id = pu.project_id
                WHERE pu.user_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            print(f"Debug - Query returned {len(results)} projects")

            for result in results:
                project = Project(
                    id=result['id'],
                    project_number=result['project_number'],
                    name=result['name'],
                    description=result['description'],
                    start_date=result['start_date'],
                    end_date=result['end_date'],
                    status=result['status'],
                    type=result['type'],
                    organization_id=result['organization_id']
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
        connection = get_db_connection('users_db')
        cursor = None
        count = 0

        try:
            cursor = connection.cursor()
            query = """
                SELECT COUNT(*) 
                FROM project_users 
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
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()

            if self.id:  # Update existing project
                query = """
                    UPDATE projects
                    SET project_number = %s, name = %s, description = %s,
                    status = %s, type = %s,
                    organization_id = NULLIF(UUID_TO_BIN(%s), UUID_TO_BIN(NULL))
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (
                    self.project_number, self.name, self.description,
                    self.status, self.type, self.organization_id, self.id
                )
            else:  # Create new project
                query = """
                    INSERT INTO projects (project_number, name, description, status, type, organization_id)
                    VALUES (%s, %s, %s, %s, %s, NULLIF(UUID_TO_BIN(%s), UUID_TO_BIN(NULL)))
                """
                values = (
                    self.project_number, self.name, self.description,
                    self.status, self.type, self.organization_id
                )

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new project
            if not self.id:
                # For UUIDs, we need to query the UUID that was just created
                cursor.execute("""
                    SELECT BIN_TO_UUID(id) 
                    FROM projects 
                    WHERE project_number = %s
                """, (self.project_number,))

                result = cursor.fetchone()
                if result:
                    self.id = result[0]

            return True
        except Exception as e:
            connection.rollback()
            print(f"Error saving project: {e}")
            import traceback
            traceback.print_exc()  # Print the full error traceback for debugging
            return False
        finally:
            close_connection(connection, cursor)

    def add_user(self, user_id):
        """Add a user to the project"""
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO project_users (project_id, user_id)
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

class Organizations:
    def __init__(self, id=None, name=None, created_at=None, super_admin_id=None):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.super_admin_id = super_admin_id

    @staticmethod
    def find_by_id(organization_id):
        """Find an organization by ID"""
        connection = get_db_connection('users_db')
        cursor = None
        organization = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, name, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organizations WHERE id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (organization_id,))
            result = cursor.fetchone()

            if result:
                organization = Organizations(
                    id=result['id'],
                    name=result['name'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
        except Exception as e:
            print(f"Error finding organization by ID: {e}")
        finally:
            close_connection(connection, cursor)

        return organization

    @staticmethod
    def find_by_name(name):
        """Find an organization by name"""
        connection = get_db_connection('users_db')
        cursor = None
        organization = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, name, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organizations WHERE name = %s
            """
            cursor.execute(query, (name,))
            result = cursor.fetchone()

            if result:
                organization = Organizations(
                    id=result['id'],
                    name=result['name'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
        except Exception as e:
            print(f"Error finding organization by name: {e}")
        finally:
            close_connection(connection, cursor)

        return organization

    @staticmethod
    def find_all():
        """Find all organizations"""
        connection = get_db_connection('users_db')
        cursor = None
        organizations = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, name, created_at, 
                BIN_TO_UUID(super_admin_id) as super_admin_id 
                FROM organizations
            """
            cursor.execute(query)
            results = cursor.fetchall()

            for result in results:
                organization = Organizations(
                    id=result['id'],
                    name=result['name'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
                organizations.append(organization)
        except Exception as e:
            print(f"Error finding all organizations: {e}")
        finally:
            close_connection(connection, cursor)

        return organizations

    @staticmethod
    def find_by_user(user_id):
        """Find all organizations for a user"""
        connection = get_db_connection('users_db')
        cursor = None
        organizations = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(o.id) as id, o.name, o.created_at, 
                BIN_TO_UUID(o.super_admin_id) as super_admin_id
                FROM organizations o
                JOIN organisation_user ou ON o.id = ou.organisations_id
                WHERE ou.users_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()

            for result in results:
                organization = Organizations(
                    id=result['id'],
                    name=result['name'],
                    created_at=result['created_at'],
                    super_admin_id=result['super_admin_id']
                )
                organizations.append(organization)
        except Exception as e:
            print(f"Error finding organizations for user: {e}")
        finally:
            close_connection(connection, cursor)

        return organizations

    def save(self):
        """Save organization to database"""
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()

            if self.id:  # Update existing organization
                query = """
                    UPDATE organizations
                    SET name = %s, super_admin_id = NULLIF(UUID_TO_BIN(%s), UUID_TO_BIN(NULL))
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (self.name, self.super_admin_id, self.id)
            else:  # Create new organization
                query = """
                    INSERT INTO organizations (name, super_admin_id)
                    VALUES (%s, NULLIF(UUID_TO_BIN(%s), UUID_TO_BIN(NULL)))
                """
                values = (self.name, self.super_admin_id)

            # Execute with the parameter that suppresses result sets
            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new organization
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
                        "SELECT BIN_TO_UUID(id) FROM organizations WHERE id = LAST_INSERT_ID()")
                    uuid_result = cursor.fetchone()
                    if uuid_result:
                        self.id = uuid_result[0]

            return True
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error saving organization: {e}")
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
        """Add a user to the organization"""
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO organization_user (organizations_id, users_id)
                VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))
            """
            cursor.execute(query, (self.id, user_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error adding user to organization: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def remove_user(self, user_id):
        """Remove a user from the organization"""
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                DELETE FROM organization_user
                WHERE organizations_id = UUID_TO_BIN(%s) AND users_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id, user_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error removing user from organization: {e}")
            return False
        finally:
            close_connection(connection, cursor)

    def get_users(self):
        """Get all users in the organization"""
        connection = get_db_connection('users_db')
        cursor = None
        users = []

        try:
            cursor = connection.cursor(dictionary=True)
            print(f"Getting users for organization ID: {self.id}")

            query = """
                SELECT BIN_TO_UUID(u.id) as id, u.last_name, u.first_name, u.email, 
                u.created_at, u.is_active
                FROM users u
                JOIN organization_user ou ON u.id = ou.users_id
                WHERE ou.organizations_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            print(f"Found {len(results)} users for organization")

            for result in results:
                # Use direct User class import from current module to avoid import issues
                user = User(
                    id=result['id'],
                    last_name=result['last_name'],
                    first_name=result['first_name'],
                    email=result['email'],
                    created_at=result['created_at'],
                    is_active=result['is_active']
                )
                users.append(user)
        except Exception as e:
            print(f"Error getting users for organization: {e}")
            # Print more detailed error information
            import traceback
            traceback.print_exc()
        finally:
            close_connection(connection, cursor)

        return users

    def get_user_roles(self, user_id):
        """Get all roles for a specific user in the organization"""
        connection = get_db_connection('users_db')
        cursor = None
        roles = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(r.id) as id, r.name, r.description, r.created_at
                FROM organization_roles r
                JOIN user_organisation_role uor ON r.id = uor.role_id
                WHERE uor.user_id = UUID_TO_BIN(%s) 
                AND uor.organization_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id, self.id))
            results = cursor.fetchall()

            for result in results:
                role = {
                    'id': result['id'],
                    'name': result['name'],
                    'description': result['description'],
                    'created_at': result['created_at']
                }
                roles.append(role)
        except Exception as e:
            print(f"Error getting roles for user {user_id} in organisation {self.id}: {e}")
        finally:
            close_connection(connection, cursor)

        return roles

    def get_projects(self):
        """Get all projects in the organisation"""
        connection = get_db_connection('users_db')
        cursor = None
        projects = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, project_number, name, description, 
                start_date, end_date, status, type
                FROM projects 
                WHERE organization_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            for result in results:
                from server.models.project import Project  # Import here to avoid circular imports
                project = Project(
                    id=result['id'],
                    project_number=result['project_number'],
                    name=result['name'],
                    description=result['description'],
                    start_date=result['start_date'],
                    end_date=result['end_date'],
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
        connection = get_db_connection('projects_db')
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO organization_roles (organization_id, name, description)
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
        connection = get_db_connection('projects_db')
        cursor = None
        roles = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, name, description, created_at
                FROM organization_roles
                WHERE organization_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            for result in results:
                role = {
                    'id': result['id'],
                    'name': result['name'],
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
        connection = get_db_connection('projects_db')
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO user_organization_roles (user_id, organization_id, role_id)
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
        connection = get_db_connection('projects_db')
        cursor = None
        roles = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(r.id) as id, r.name, r.description, r.created_at
                FROM organization_roles r
                JOIN user_organisation_role uor ON r.id = uor.role_id
                WHERE uor.user_id = UUID_TO_BIN(%s) AND uor.organisation_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id, self.id))
            results = cursor.fetchall()

            for result in results:
                role = {
                    'id': result['id'],
                    'name': result['name'],
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
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()
            query = """
                DELETE FROM organizations
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