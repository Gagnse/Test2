import uuid
import bcrypt
import secrets
import datetime
from server.database.db_config import get_db_connection, close_connection
from server.utils.database_utils import *


class User:
    def __init__(self, id=None, first_name=None, last_name=None, email=None, password=None,
                 created_at=None, is_active=True, organization_id=None, department=None,
                 location=None, role=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.created_at = created_at
        self.is_active = is_active
        self.organization_id = organization_id
        self.department = department
        self.location = location
        self.role = role

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
                BIN_TO_UUID(organization_id) as organization_id,
                department, location, role  # Ensure these fields are included
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
                    organization_id=result['organization_id'],
                    department=result.get('department'),
                    location=result.get('location'),
                    role=result.get('role')
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

            if self.id:  # Update existing user
                query = """
                    UPDATE users
                    SET first_name = %s, last_name = %s, email = %s,
                    is_active = %s, department = %s, location = %s, role = %s
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (
                    self.first_name, self.last_name, self.email,
                    self.is_active,
                    getattr(self, 'department', None),
                    getattr(self, 'location', None),
                    getattr(self, 'role', None),
                    self.id
                )
            else:  # Create new user
                # Hash the password for new users
                hashed_password = self.hash_password(self.password)

                # Handle case where organization_id is provided
                org_id_param = self.organization_id if hasattr(self,
                                                               'organization_id') and self.organization_id else None

                query = """
                    INSERT INTO users (first_name, last_name, email, password, 
                                       organization_id, department, location, role, is_active)
                    VALUES (%s, %s, %s, %s, UUID_TO_BIN(%s), %s, %s, %s, %s)
                """
                values = (
                    self.first_name, self.last_name, self.email,
                    hashed_password, org_id_param,
                    getattr(self, 'department', None),
                    getattr(self, 'location', None),
                    getattr(self, 'role', None),
                    self.is_active
                )

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new user
            if not self.id:
                cursor.execute("""
                    SELECT BIN_TO_UUID(id) 
                    FROM users 
                    WHERE email = %s
                """, (self.email,))

                result = cursor.fetchone()
                if result:
                    self.id = result[0]

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


    @staticmethod
    def is_super_admin(user_id, organization_id):
        """Check if the user is the super admin of the organization"""
        connection = get_db_connection('users_db')
        cursor = None
        is_admin = False

        try:
            cursor = connection.cursor()
            query = """
                SELECT COUNT(*) 
                FROM organizations 
                WHERE id = UUID_TO_BIN(%s) AND super_admin_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (organization_id, user_id))
            result = cursor.fetchone()
            is_admin = result[0] > 0 if result else False
        except Exception as e:
            print(f"Error checking super admin status: {e}")
        finally:
            close_connection(connection, cursor)

        return is_admin

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
            #print(f"Debug - Finding projects for user ID: {user_id}")

            query = """
                SELECT BIN_TO_UUID(p.id) as id, p.project_number, p.name, p.description, 
                p.start_date, p.end_date, p.status, p.type, BIN_TO_UUID(p.organization_id) as organization_id
                FROM projects p
                JOIN project_users pu ON p.id = pu.project_id
                WHERE pu.user_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            #print(f"Debug - Query returned {len(results)} projects")

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

                    # Create project database using Python function
                    try:
                        # Import the function here to avoid circular imports
                        from server.utils.database_utils import create_project_database

                        # Call the Python function to create the database with UUID
                        result = create_project_database(self.id, self.project_number)

                        if result:
                            print(f"Project database for project {self.id} created successfully")
                        else:
                            print(f"Failed to create project database for project {self.id}")
                    except Exception as e:
                        print(f"Error creating project database: {e}")
                        # Continue anyway, since the project itself was created successfully

            return True
        except Exception as e:
            connection.rollback()
            print(f"Error saving project: {e}")
            import traceback
            traceback.print_exc()  # Print the full error traceback for debugging
            return False
        finally:
            close_connection(connection, cursor)

    def save_image(self, image_file):
        """Save project image and update image_url field"""
        # Create unique filename using project ID
        filename = f"project_{self.id}.{image_file.filename.split('.')[-1]}"

        # Define path to save
        save_path = os.path.join('frontend', 'static', 'uploads', 'project_images', filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the file
        image_file.save(save_path)

        # Update the image_url in database
        self.image_url = f"/static/uploads/project_images/{filename}"
        self.save()  # Save to database

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
                JOIN organization_user ou ON o.id = ou.organizations_id
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
            #print(f"Getting users for organization ID: {self.id}")

            query = """
                 SELECT BIN_TO_UUID(u.id) as id, u.last_name, u.first_name, u.email, 
                 u.created_at, u.is_active, u.department, u.location, u.role
                 FROM users u
                 JOIN organization_user ou ON u.id = ou.users_id
                 WHERE ou.organizations_id = UUID_TO_BIN(%s)
             """
            cursor.execute(query, (self.id,))
            results = cursor.fetchall()

            #print(f"Found {len(results)} users for organization")

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
                # Also set these attributes separately
                if 'department' in result:
                    user.department = result['department']
                if 'location' in result:
                    user.location = result['location']
                if 'role' in result:
                    user.role = result['role']
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
        connection = get_db_connection('users_db')  # Use users_db, not project_db
        cursor = None
        roles = []

        try:
            # First check if user is super admin - this takes precedence over assigned roles
            if User.is_super_admin(user_id, self.id):
                # Return Administrateur role for super admins
                #print(f"User {user_id} is super admin of organization {self.id}, returning Administrateur role")
                return [{'id': 'super-admin', 'name': 'Administrateur', 'description': 'Super Administrator'}]

            # Get role IDs from user_organisation_role table
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT r.id, r.name, r.description, r.created_at
                FROM organization_roles r
                JOIN user_organisation_role uor ON r.id = uor.role_id
                WHERE uor.user_id = UUID_TO_BIN(%s) 
                AND uor.organisation_id = UUID_TO_BIN(%s)
            """
            cursor.execute(query, (user_id, self.id))
            results = cursor.fetchall()

            if results:
                for result in results:
                    role = {
                        'id': result['id'],
                        'name': result['name'],
                        'description': result['description'],
                        'created_at': result['created_at']
                    }
                    roles.append(role)
                    #print(f"Found assigned role {result['name']} for user {user_id}")
        except Exception as e:
            print(f"Error getting roles for user {user_id} in organization {self.id}: {e}")
            import traceback
            traceback.print_exc()
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
                # Import Project class locally to avoid circular imports
                from server.database.models import Project
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
            print(f"Error getting projects for organization: {e}")
        finally:
            close_connection(connection, cursor)

        return projects

    def get_roles(self):
        """Get all roles in the organization"""
        connection = get_db_connection('project_db')
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
            print(f"Error getting roles for organization: {e}")
        finally:
            close_connection(connection, cursor)

        return roles

    def assign_role_to_user(self, user_id, role_id):
        """Assign a role to a user in the organization"""
        connection = get_db_connection('project_db')
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

    def delete(self):
        """Delete the organization"""
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
            print(f"Error deleting organization: {e}")
            return False
        finally:
            close_connection(connection, cursor)


class Invitation:
    def __init__(self, id=None, organization_id=None, email=None, first_name=None, last_name=None,
                 role=None, department=None, location=None, token=None, invited_by=None,
                 created_at=None, expires_at=None, status='pending'):
        self.id = id
        self.organization_id = organization_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.department = department
        self.location = location
        self.token = token or secrets.token_urlsafe(64)
        self.invited_by = invited_by
        self.created_at = created_at
        # Default expiration is 7 days from now
        self.expires_at = expires_at or (datetime.datetime.now() + datetime.timedelta(days=7))
        self.status = status

    @staticmethod
    def create(organization_id, email, first_name, last_name, role, invited_by,
               department=None, location=None, expires_in_days=7):
        """Create a new invitation and save it to the database"""
        # Generate expiration date
        expires_at = datetime.datetime.now() + datetime.timedelta(days=expires_in_days)

        # Create new invitation
        invitation = Invitation(
            organization_id=organization_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department,
            location=location,
            invited_by=invited_by,
            expires_at=expires_at
        )

        # Save to database and return the invitation with ID
        if invitation.save():
            return invitation
        return None

    def save(self):
        """Save invitation to database"""
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()

            if self.id:  # Update existing invitation
                query = """
                    UPDATE organization_invitations
                    SET email = %s, first_name = %s, last_name = %s, role = %s,
                        department = %s, location = %s, status = %s, expires_at = %s
                    WHERE id = UUID_TO_BIN(%s)
                """
                values = (
                    self.email, self.first_name, self.last_name, self.role,
                    self.department, self.location, self.status, self.expires_at,
                    self.id
                )
            else:  # Create new invitation
                query = """
                    INSERT INTO organization_invitations (
                        organization_id, email, first_name, last_name, role,
                        department, location, token, invited_by, expires_at
                    ) VALUES (
                        UUID_TO_BIN(%s), %s, %s, %s, %s, %s, %s, %s, UUID_TO_BIN(%s), %s
                    )
                """
                values = (
                    self.organization_id, self.email, self.first_name, self.last_name, self.role,
                    self.department, self.location, self.token, self.invited_by, self.expires_at
                )

            cursor.execute(query, values)
            connection.commit()

            # Get the auto-generated ID for a new invitation
            if not self.id:
                cursor.execute("""
                    SELECT BIN_TO_UUID(id) 
                    FROM organization_invitations 
                    WHERE email = %s AND organization_id = UUID_TO_BIN(%s) AND token = %s
                """, (self.email, self.organization_id, self.token))

                result = cursor.fetchone()
                if result:
                    self.id = result[0]

            return True
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error saving invitation: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            close_connection(connection, cursor)

    @staticmethod
    def find_by_token(token):
        """Find an invitation by token"""
        connection = get_db_connection('users_db')
        cursor = None
        invitation = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, BIN_TO_UUID(organization_id) as organization_id,
                email, first_name, last_name, role, department, location, token,
                BIN_TO_UUID(invited_by) as invited_by, created_at, expires_at, status
                FROM organization_invitations
                WHERE token = %s
            """
            cursor.execute(query, (token,))
            result = cursor.fetchone()

            if result:
                invitation = Invitation(
                    id=result['id'],
                    organization_id=result['organization_id'],
                    email=result['email'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    role=result['role'],
                    department=result['department'],
                    location=result['location'],
                    token=result['token'],
                    invited_by=result['invited_by'],
                    created_at=result['created_at'],
                    expires_at=result['expires_at'],
                    status=result['status']
                )
        except Exception as e:
            print(f"Error finding invitation by token: {e}")
        finally:
            close_connection(connection, cursor)

        return invitation

    @staticmethod
    def find_by_email_and_org(email, organization_id):
        """Find a pending invitation by email and organization"""
        connection = get_db_connection('users_db')
        cursor = None
        invitation = None

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, BIN_TO_UUID(organization_id) as organization_id,
                email, first_name, last_name, role, department, location, token,
                BIN_TO_UUID(invited_by) as invited_by, created_at, expires_at, status
                FROM organization_invitations
                WHERE email = %s AND organization_id = UUID_TO_BIN(%s) AND status = 'pending'
            """
            cursor.execute(query, (email, organization_id))
            result = cursor.fetchone()

            if result:
                invitation = Invitation(
                    id=result['id'],
                    organization_id=result['organization_id'],
                    email=result['email'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    role=result['role'],
                    department=result['department'],
                    location=result['location'],
                    token=result['token'],
                    invited_by=result['invited_by'],
                    created_at=result['created_at'],
                    expires_at=result['expires_at'],
                    status=result['status']
                )
        except Exception as e:
            print(f"Error finding invitation by email and org: {e}")
        finally:
            close_connection(connection, cursor)

        return invitation

    def accept(self):
        """Mark invitation as accepted"""
        self.status = 'accepted'
        return self.save()

    def cancel(self):
        """Mark invitation as cancelled"""
        self.status = 'cancelled'
        return self.save()

    def expire(self):
        """Mark invitation as expired"""
        self.status = 'expired'
        return self.save()

    def is_expired(self):
        """Check if the invitation is expired"""
        return datetime.datetime.now() > self.expires_at or self.status == 'expired'

    def is_valid(self):
        """Check if the invitation is valid for acceptance"""
        return self.status == 'pending' and not self.is_expired()

    @staticmethod
    def get_pending_invitations_for_organization(organization_id):
        """Get all pending invitations for an organization"""
        connection = get_db_connection('users_db')
        cursor = None
        invitations = []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT BIN_TO_UUID(id) as id, BIN_TO_UUID(organization_id) as organization_id,
                email, first_name, last_name, role, department, location, token,
                BIN_TO_UUID(invited_by) as invited_by, created_at, expires_at, status
                FROM organization_invitations
                WHERE organization_id = UUID_TO_BIN(%s) AND status = 'pending'
                ORDER BY created_at DESC
            """
            cursor.execute(query, (organization_id,))
            results = cursor.fetchall()

            for result in results:
                invitation = Invitation(
                    id=result['id'],
                    organization_id=result['organization_id'],
                    email=result['email'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    role=result['role'],
                    department=result['department'],
                    location=result['location'],
                    token=result['token'],
                    invited_by=result['invited_by'],
                    created_at=result['created_at'],
                    expires_at=result['expires_at'],
                    status=result['status']
                )
                invitations.append(invitation)
        except Exception as e:
            print(f"Error getting pending invitations: {e}")
        finally:
            close_connection(connection, cursor)

        return invitations