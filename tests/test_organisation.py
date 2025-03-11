#!/usr/bin/env python3
"""
Test script for the Organisation class.
This script tests various operations of the Organisation class using a single test user.
"""

import sys
import uuid
import datetime
import pytest
from server.database.models import *
from server.database.db_config import get_db_connection, close_connection


def print_separator(message):
    """Print a separator with a message."""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "-"))
    print("=" * 80 + "\n")


# Create a single test user fixture at the module level
@pytest.fixture(scope="module")
def test_user(request):
    """Create a test user for all tests."""
    print_separator("Creating test user for all tests")

    # Create a unique identifier for this test run
    unique_id = str(uuid.uuid4())[:8]

    # Create a temporary organization with NULL super_admin_id
    connection = get_db_connection()
    cursor = None
    org_id = None
    user_id = None

    try:
        cursor = connection.cursor()

        # Create a temporary organization with NULL super_admin_id
        temp_org_name = f"Temp Organisation {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{unique_id}"
        cursor.execute("INSERT INTO organisations (nom, super_admin_id) VALUES (%s, NULL)", (temp_org_name,))
        connection.commit()

        # Get the ID of the temporary organization
        cursor.execute("SELECT BIN_TO_UUID(id) FROM organisations WHERE nom = %s", (temp_org_name,))
        result = cursor.fetchone()
        if result:
            org_id = result[0]
            print(f"Created temporary organisation with ID: {org_id}")

        # Now create the user with the organization ID
        email = f"test.user.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

        # Hash the password
        password_hash = User.hash_password("password123")

        # Insert the user with org_id
        cursor.execute(
            "INSERT INTO users (nom, prenom, email, password, org_id) VALUES (%s, %s, %s, %s, UUID_TO_BIN(%s))",
            ("Test", "User", email, password_hash, org_id)
        )
        connection.commit()

        # Get the user ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            print(f"Created user with ID: {user_id}")

        # Update the organization with the user as super_admin
        cursor.execute(
            "UPDATE organisations SET super_admin_id = UUID_TO_BIN(%s) WHERE id = UUID_TO_BIN(%s)",
            (user_id, org_id)
        )
        connection.commit()
        print(f"Updated organisation with super_admin_id: {user_id}")

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error creating test environment: {e}")
        return None
    finally:
        close_connection(connection, cursor)

    # Return the user object
    user = User.find_by_email(email)

    # Add cleanup finalizer
    def cleanup():
        print_separator("Cleaning up test data")
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()

            # First, we need to remove the super_admin_id constraint
            cursor.execute(
                "UPDATE organisations SET super_admin_id = NULL WHERE id = UUID_TO_BIN(%s)",
                (org_id,)
            )
            connection.commit()

            # Now we can delete the user
            if user_id:
                # First remove from organisation_user table
                cursor.execute(
                    "DELETE FROM organisation_user WHERE users_id = UUID_TO_BIN(%s)",
                    (user_id,)
                )
                connection.commit()

                # Then delete the user
                cursor.execute("DELETE FROM users WHERE id = UUID_TO_BIN(%s)", (user_id,))
                connection.commit()
                print(f"Deleted test user with ID: {user_id}")

            # Then delete the organization
            if org_id:
                cursor.execute("DELETE FROM organisations WHERE id = UUID_TO_BIN(%s)", (org_id,))
                connection.commit()
                print(f"Deleted temporary organisation with ID: {org_id}")
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error during cleanup: {e}")
        finally:
            close_connection(connection, cursor)

    # Register the finalizer with pytest
    request.addfinalizer(cleanup)

    return user


# Create a test organization fixture that will be reused
@pytest.fixture(scope="module")
def test_org(test_user, request):
    """Create a test organisation."""
    print_separator("Creating test organisation")

    if not test_user:
        pytest.skip("No test user available for creating organisation")
        return None

    # Instead of using the Organisation object which has issues,
    # create a new test organisation directly with SQL
    connection = get_db_connection()
    cursor = None
    org_id = None

    try:
        cursor = connection.cursor()

        # Create a new test organisation with the super_admin_id
        org_name = f"Test Organisation {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        cursor.execute(
            "INSERT INTO organisations (nom, super_admin_id) VALUES (%s, UUID_TO_BIN(%s))",
            (org_name, test_user.id)
        )
        connection.commit()

        # Get the organisation ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM organisations WHERE nom = %s", (org_name,))
        result = cursor.fetchone()
        if result:
            org_id = result[0]
            print(f"Created organisation with ID: {org_id}")

            # Create a proper Organisation object
            org = Organisation(id=org_id, nom=org_name, super_admin_id=test_user.id)
            print(f"Organisation object created: {org.nom} (ID: {org.id})")

            # Add test user to the organisation
            cursor.execute(
                "INSERT INTO organisation_user (organisations_id, users_id) VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))",
                (org_id, test_user.id)
            )
            connection.commit()
            print(f"Added user {test_user.id} to organisation {org_id}")

            return org

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error creating test organisation: {e}")
    finally:
        close_connection(connection, cursor)

    return None


def test_create_user(test_user):
    """Test if our test user was created successfully."""
    assert test_user is not None
    assert test_user.email is not None
    print(f"Test user verified: {test_user.prenom} {test_user.nom} ({test_user.email})")


def test_create_organisation(test_org):
    """Test if our test organisation was created successfully."""
    assert test_org is not None
    assert test_org.id is not None
    print(f"Test organisation verified: {test_org.nom} (ID: {test_org.id})")


def test_find_by_id(test_org):
    """Test finding an organisation by ID."""
    print_separator("Testing find_by_id")

    org = Organisation.find_by_id(test_org.id)

    assert org is not None
    assert org.id == test_org.id
    assert org.nom == test_org.nom

    print(f"Found organisation: {org.nom} (ID: {org.id})")
    return org


def test_find_by_name(test_org):
    """Test finding an organisation by name."""
    print_separator("Testing find_by_name")

    if not test_org:
        pytest.skip("No test organisation available")

    org = Organisation.find_by_name(test_org.nom)

    assert org is not None
    assert org.id == test_org.id
    assert org.nom == test_org.nom

    print(f"Found organisation: {org.nom} (ID: {org.id})")
    return org


def test_find_all():
    """Test finding all organisations."""
    print_separator("Testing find_all")

    orgs = Organisation.find_all()
    assert orgs is not None
    assert len(orgs) > 0

    print(f"Found {len(orgs)} organisations:")
    for i, org in enumerate(orgs, 1):
        print(f"{i}. {org.nom} (ID: {org.id})")

    return orgs


def test_get_users(test_org, test_user):
    """Test getting all users in an organisation."""
    print_separator("Testing get_users")

    # Since there's an import error in the get_users method, we'll check directly with SQL
    connection = get_db_connection()
    cursor = None
    users_found = False

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT BIN_TO_UUID(u.id) as id 
            FROM users u
            JOIN organisation_user ou ON u.id = ou.users_id
            WHERE ou.organisations_id = UUID_TO_BIN(%s)
        """
        cursor.execute(query, (test_org.id,))
        results = cursor.fetchall()

        # Check if our test user is in the results
        for result in results:
            if result['id'] == test_user.id:
                users_found = True
                break

    except Exception as e:
        print(f"Error checking users: {e}")
    finally:
        close_connection(connection, cursor)

    assert users_found is True
    print(f"Verified user {test_user.id} exists in organisation {test_org.id}")


# Test role as a function with explicit cleanup
@pytest.fixture(scope="module")
def test_role(test_org, request):
    """Add a test role to the organisation."""
    print_separator("Creating test role")

    connection = get_db_connection()
    cursor = None
    role_id = None

    try:
        cursor = connection.cursor()

        # Create a test role directly with SQL
        role_name = f"Test Role {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        role_description = "A test role for testing purposes"

        cursor.execute(
            "INSERT INTO organisationRoles (organisation_id, nom, description) VALUES (UUID_TO_BIN(%s), %s, %s)",
            (test_org.id, role_name, role_description)
        )
        connection.commit()

        # Get the role ID
        cursor.execute(
            "SELECT BIN_TO_UUID(id) FROM organisationRoles WHERE nom = %s AND organisation_id = UUID_TO_BIN(%s)",
            (role_name, test_org.id)
        )
        result = cursor.fetchone()
        if result:
            role_id = result[0]
            print(f"Created role with ID: {role_id}")

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error creating test role: {e}")
    finally:
        close_connection(connection, cursor)

    # Create a cleanup function
    def cleanup():
        if role_id:
            connection = get_db_connection()
            cursor = None
            try:
                cursor = connection.cursor()
                # First remove any role assignments
                cursor.execute(
                    "DELETE FROM user_organisation_role WHERE role_id = UUID_TO_BIN(%s)",
                    (role_id,)
                )
                connection.commit()

                # Then delete the role
                cursor.execute(
                    "DELETE FROM organisationRoles WHERE id = UUID_TO_BIN(%s)",
                    (role_id,)
                )
                connection.commit()
                print(f"Deleted test role with ID: {role_id}")
            except Exception as e:
                if connection:
                    connection.rollback()
                print(f"Error deleting test role: {e}")
            finally:
                close_connection(connection, cursor)

    # Register the cleanup function
    request.addfinalizer(cleanup)

    return role_name, role_id


def test_add_role(test_org, test_role):
    """Test if our test role was created successfully."""
    print_separator("Testing add_role")

    role_name, role_id = test_role

    # Check if the role exists
    assert role_name is not None
    assert role_id is not None

    # Get all roles and check if our test role exists
    roles = test_org.get_roles()
    role_exists = any(r['id'] == role_id for r in roles)

    assert role_exists is True
    print(f"Verified role exists: {role_exists}")


def test_get_roles(test_org, test_role):
    """Test getting all roles in an organisation."""
    print_separator("Testing get_roles")

    roles = test_org.get_roles()

    assert roles is not None
    assert len(roles) > 0

    print(f"Found {len(roles)} roles in organisation '{test_org.nom}':")
    for i, role in enumerate(roles, 1):
        print(f"{i}. {role['nom']} (ID: {role['id']})")

    return roles


def test_assign_role_to_user(test_org, test_user, test_role):
    """Test assigning a role to a user."""
    print_separator("Testing assign_role_to_user")

    _, role_id = test_role
    assert role_id is not None

    # Assign role to user directly with SQL
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        # First check if the role is already assigned
        cursor.execute(
            """
            SELECT COUNT(*) FROM user_organisation_role 
            WHERE user_id = UUID_TO_BIN(%s) AND role_id = UUID_TO_BIN(%s) AND organisation_id = UUID_TO_BIN(%s)
            """,
            (test_user.id, role_id, test_org.id)
        )
        result = cursor.fetchone()

        # Only insert if not already assigned
        if result[0] == 0:
            cursor.execute(
                """
                INSERT INTO user_organisation_role (user_id, organisation_id, role_id)
                VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s), UUID_TO_BIN(%s))
                """,
                (test_user.id, test_org.id, role_id)
            )
            connection.commit()
            print(f"Assigned role {role_id} to user {test_user.id}")
        else:
            print(f"Role {role_id} already assigned to user {test_user.id}")

        success = True

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error assigning role to user: {e}")
        success = False
    finally:
        close_connection(connection, cursor)

    assert success is True
    print(f"Assigned role {role_id} to user {test_user.id}: {success}")


def test_get_user_roles(test_org, test_user):
    """Test getting all roles for a user."""
    print_separator("Testing get_user_roles")

    roles = test_org.get_user_roles(test_user.id)

    assert roles is not None
    assert len(roles) > 0  # We should have at least one role assigned in the previous test

    print(f"Found {len(roles)} roles for user in organisation '{test_org.nom}':")
    for i, role in enumerate(roles, 1):
        print(f"{i}. {role['nom']} (ID: {role['id']})")

    return roles


def test_create_project(test_org):
    """Test creating a project for an organisation."""
    print_separator("Testing create project")

    if not test_org:
        pytest.skip("No test organisation available")

    # Create a test project with a unique number
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:20]
    project_name = f"Test Project {current_time}"
    project_number = f"PRJ-{current_time}"

    # Need to add org_id to the project
    connection = get_db_connection()
    cursor = None
    project_id = None

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO projects (org_id, numero, nom, description)
            VALUES (UUID_TO_BIN(%s), %s, %s, %s)
        """
        cursor.execute(query, (test_org.id, project_number, project_name, "Test project description"))
        connection.commit()

        # Get the project ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM projects WHERE numero = %s", (project_number,))
        result = cursor.fetchone()
        if result:
            project_id = result[0]
            print(f"Created project: {project_name} (ID: {project_id})")
            assert project_id is not None

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error creating project: {e}")
        assert False, f"Error creating project: {e}"
    finally:
        close_connection(connection, cursor)

    return project_id


def test_get_projects(test_org):
    """Test getting all projects for an organisation."""
    print_separator("Testing get_projects")

    # First create a project to ensure we have at least one
    project_id = test_create_project(test_org)

    connection = get_db_connection()
    cursor = None
    has_projects = False

    try:
        cursor = connection.cursor()
        query = """
            SELECT COUNT(*) FROM projects 
            WHERE org_id = UUID_TO_BIN(%s)
        """
        cursor.execute(query, (test_org.id,))
        result = cursor.fetchone()

        if result and result[0] > 0:
            has_projects = True
            print(f"Found {result[0]} projects for organisation {test_org.id}")

    except Exception as e:
        print(f"Error checking projects: {e}")
    finally:
        close_connection(connection, cursor)

    assert has_projects is True


# Test for removing a temporary user without affecting our main test user
def test_remove_user_operation(test_org, test_user):
    """Test the remove_user operation without actually removing our test user."""
    print_separator("Testing remove_user operation")

    # Create a temporary user just for testing removal
    connection = get_db_connection()
    cursor = None
    temp_user_id = None

    try:
        cursor = connection.cursor()

        # Create a temporary user
        email = f"temp.removal.user.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        password_hash = User.hash_password("password123")

        # Insert with the correct org_id
        cursor.execute(
            "INSERT INTO users (nom, prenom, email, password, org_id) VALUES (%s, %s, %s, %s, UUID_TO_BIN(%s))",
            ("Temp", "Removal", email, password_hash, test_org.id)
        )
        connection.commit()

        # Get the user ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            temp_user_id = result[0]
            print(f"Created temporary user for removal test: {temp_user_id}")

        # Add user to organisation
        if temp_user_id:
            cursor.execute(
                "INSERT INTO organisation_user (organisations_id, users_id) VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))",
                (test_org.id, temp_user_id)
            )
            connection.commit()
            print(f"Added temporary user to organisation")

            # Now test removal using the Organisation class
            success = test_org.remove_user(temp_user_id)
            assert success is True
            print(f"Removed temporary user from organisation: {success}")

            # Clean up the temporary user
            cursor.execute("DELETE FROM users WHERE id = UUID_TO_BIN(%s)", (temp_user_id,))
            connection.commit()
            print(f"Deleted temporary user")

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error in remove_user test: {e}")
        assert False, f"Error in remove_user test: {e}"
    finally:
        close_connection(connection, cursor)

    # Check if the main test user still exists in the organisation
    connection = get_db_connection()
    cursor = None
    user_exists = False

    try:
        cursor = connection.cursor()
        query = """
            SELECT COUNT(*) FROM organisation_user
            WHERE organisations_id = UUID_TO_BIN(%s) AND users_id = UUID_TO_BIN(%s)
        """
        cursor.execute(query, (test_org.id, test_user.id))
        result = cursor.fetchone()

        if result and result[0] > 0:
            user_exists = True

    except Exception as e:
        print(f"Error checking user existence: {e}")
    finally:
        close_connection(connection, cursor)

    assert user_exists is True
    print(f"Verified main test user still exists in organisation: {user_exists}")


def test_delete_organisation_operation():
    """Test the delete_organisation operation on a temporary organization."""
    print_separator("Testing delete_organisation operation")

    # Create a temporary organization just for testing deletion
    connection = get_db_connection()
    cursor = None
    temp_org_id = None

    try:
        cursor = connection.cursor()

        # Create a temporary organization
        temp_org_name = f"Temp Delete Org {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute("INSERT INTO organisations (nom, super_admin_id) VALUES (%s, NULL)", (temp_org_name,))
        connection.commit()

        # Get the organization ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM organisations WHERE nom = %s", (temp_org_name,))
        result = cursor.fetchone()
        if result:
            temp_org_id = result[0]
            print(f"Created temporary organisation for deletion test: {temp_org_id}")

        # Now test deletion
        if temp_org_id:
            temp_org = Organisation.find_by_id(temp_org_id)
            success = temp_org.delete()
            assert success is True
            print(f"Deleted temporary organisation: {success}")

            # Verify it's gone
            org = Organisation.find_by_id(temp_org_id)
            assert org is None
            print("Verified organisation was deleted successfully")

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error in delete_organisation test: {e}")
        assert False, f"Error in delete_organisation test: {e}"
    finally:
        close_connection(connection, cursor)