#!/usr/bin/env python3
"""
Test script for the AuthService class.
This script tests various operations of the AuthService class including user registration,
login, logout, and authentication status checks.
"""

import sys
import uuid
import datetime
import pytest
from unittest.mock import patch, MagicMock
from flask import session
from server.database.models import User
from server.database.db_config import get_db_connection, close_connection
# Import the AuthService from services.auth
from server.services.auth import AuthService


def print_separator(message):
    """Print a separator with a message."""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "-"))
    print("=" * 80 + "\n")


# Create a test user fixture at the module level
@pytest.fixture(scope="module")
def test_user(request):
    """Create a test user for all tests."""
    print_separator("Creating test user for all auth tests")

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
        temp_org_name = f"Temp Auth Test Org {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{unique_id}"
        # Updated table name from organisations to organizations
        cursor.execute("INSERT INTO organizations (name, super_admin_id) VALUES (%s, NULL)", (temp_org_name,))
        connection.commit()

        # Get the ID of the temporary organization
        # Updated table name from organisations to organizations
        cursor.execute("SELECT BIN_TO_UUID(id) FROM organizations WHERE name = %s", (temp_org_name,))
        result = cursor.fetchone()
        if result:
            org_id = result[0]
            print(f"Created temporary organisation with ID: {org_id}")

        # Now create the user with the organization ID
        email = f"auth.test.user.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

        # Hash the password
        password_hash = User.hash_password("password123")

        # Updated field names to match SPACELOGIC_SEB.sql schema
        cursor.execute(
            "INSERT INTO users (last_name, first_name, email, password, organization_id) VALUES (%s, %s, %s, %s, UUID_TO_BIN(%s))",
            ("Auth", "TestUser", email, password_hash, org_id)
        )
        connection.commit()

        # Get the user ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            print(f"Created test user with ID: {user_id}")

        # Update the organization with the user as super_admin
        cursor.execute(
            "UPDATE organizations SET super_admin_id = UUID_TO_BIN(%s) WHERE id = UUID_TO_BIN(%s)",
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

    # Return the user object along with credentials
    user = User.find_by_email(email)
    user_data = {
        'user': user,
        'email': email,
        'password': 'password123',
        'org_id': org_id
    }

    # Add cleanup finalizer
    def cleanup():
        print_separator("Cleaning up auth test data")
        connection = get_db_connection()
        cursor = None
        try:
            cursor = connection.cursor()

            # First, we need to remove the super_admin_id constraint
            cursor.execute(
                "UPDATE organizations SET super_admin_id = NULL WHERE id = UUID_TO_BIN(%s)",
                (org_id,)
            )
            connection.commit()

            # Now we can delete the user
            if user_id:
                # First remove from organization_user table if exists (updated table name)
                cursor.execute(
                    "DELETE FROM organization_user WHERE users_id = UUID_TO_BIN(%s)",
                    (user_id,)
                )
                connection.commit()

                # Then delete the user
                cursor.execute("DELETE FROM users WHERE id = UUID_TO_BIN(%s)", (user_id,))
                connection.commit()
                print(f"Deleted test user with ID: {user_id}")

            # Then delete the organization
            if org_id:
                cursor.execute("DELETE FROM organizations WHERE id = UUID_TO_BIN(%s)", (org_id,))
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

    return user_data


# Mock Flask session for testing
@pytest.fixture
def mock_session():
    """Mock the Flask session."""
    with patch('server.services.auth.session', dict()) as mock_session:
        yield mock_session


@pytest.mark.usefixtures("mock_session")
class TestAuthService:
    """Test class for the AuthService."""

    def test_register_user_success(self):
        """Test registering a new user successfully."""
        print_separator("Testing user registration - success case")

        # Generate unique email
        unique_email = f"new.user.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

        # Mock the User.find_by_email and User.save methods
        with patch.object(User, 'find_by_email', return_value=None) as mock_find:
            with patch.object(User, 'save', return_value=True) as mock_save:
                success, message = AuthService.register_user(
                    last_name="New",
                    first_name="User",
                    email=unique_email,
                    password="securepass123"
                )

                assert success is True
                assert "réussie" in message
                mock_find.assert_called_once_with(unique_email)
                mock_save.assert_called_once()
                print(f"Registration success test passed. Message: {message}")

    def test_register_user_existing_email(self):
        """Test registering a user with an existing email."""
        print_separator("Testing user registration - existing email case")

        # Mock an existing user
        mock_user = MagicMock()
        mock_user.email = "existing@example.com"

        # Mock the User.find_by_email method to return our mock user
        with patch.object(User, 'find_by_email', return_value=mock_user) as mock_find:
            success, message = AuthService.register_user(
                last_name="Existing",
                first_name="User",
                email="existing@example.com",
                password="password123"
            )

            assert success is False
            assert "existe déjà" in message
            mock_find.assert_called_once_with("existing@example.com")
            print(f"Registration existing email test passed. Message: {message}")

    def test_register_user_save_error(self):
        """Test registering a user with a save error."""
        print_separator("Testing user registration - save error case")

        # Generate unique email
        unique_email = f"error.user.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

        # Mock the User.find_by_email method to return None (user doesn't exist)
        # and User.save method to return False (save error)
        with patch.object(User, 'find_by_email', return_value=None) as mock_find:
            with patch.object(User, 'save', return_value=False) as mock_save:
                success, message = AuthService.register_user(
                    last_name="Error",
                    first_name="User",
                    email=unique_email,
                    password="password123"
                )

                assert success is False
                assert "erreur" in message
                mock_find.assert_called_once_with(unique_email)
                mock_save.assert_called_once()
                print(f"Registration save error test passed. Message: {message}")

    def test_login_user_success(self, test_user, mock_session):
        """Test logging in a user successfully."""
        print_separator("Testing user login - success case")

        # Extract test user data
        if not test_user:
            pytest.skip("Test user not created successfully")

        user = test_user['user']
        email = test_user['email']
        password = test_user['password']

        # Mock the User.find_by_email and User.check_password methods
        with patch.object(User, 'find_by_email', return_value=user) as mock_find:
            with patch.object(User, 'check_password', return_value=True) as mock_check:
                success, message, logged_user = AuthService.login_user(email, password)

                assert success is True
                assert "réussie" in message
                assert logged_user == user
                assert mock_session['user_id'] == user.id
                assert mock_session['user_email'] == user.email
                assert mock_session['user_name'] == f"{user.first_name} {user.last_name}"

                mock_find.assert_called_once_with(email)
                mock_check.assert_called_once_with(user.password, password)
                print(f"Login success test passed. Message: {message}")

    def test_login_user_not_found(self):
        """Test logging in a user that doesn't exist."""
        print_separator("Testing user login - user not found case")

        # Mock the User.find_by_email method to return None (user doesn't exist)
        with patch.object(User, 'find_by_email', return_value=None) as mock_find:
            success, message, user = AuthService.login_user(
                email="nonexistent@example.com",
                password="password123"
            )

            assert success is False
            assert "incorrect" in message
            assert user is None
            mock_find.assert_called_once_with("nonexistent@example.com")
            print(f"Login user not found test passed. Message: {message}")

    def test_login_user_inactive(self, test_user):
        """Test logging in an inactive user."""
        print_separator("Testing user login - inactive user case")

        if not test_user:
            pytest.skip("Test user not created successfully")

        # Extract test user data and make a copy to modify
        user = test_user['user']
        email = test_user['email']
        password = test_user['password']

        # Create a modified version of the user with inactive status
        inactive_user = MagicMock()
        inactive_user.id = user.id
        inactive_user.email = email
        inactive_user.password = user.password
        inactive_user.is_active = False

        # Mock the User.find_by_email method to return our inactive user
        with patch.object(User, 'find_by_email', return_value=inactive_user) as mock_find:
            success, message, user = AuthService.login_user(email, password)

            assert success is False
            assert "désactivé" in message
            assert user is None
            mock_find.assert_called_once_with(email)
            print(f"Login inactive user test passed. Message: {message}")

    def test_login_user_wrong_password(self, test_user):
        """Test logging in with the wrong password."""
        print_separator("Testing user login - wrong password case")

        if not test_user:
            pytest.skip("Test user not created successfully")

        # Extract test user data
        user = test_user['user']
        email = test_user['email']

        # Mock the User.find_by_email method to return our test user
        # and User.check_password method to return False (wrong password)
        with patch.object(User, 'find_by_email', return_value=user) as mock_find:
            with patch.object(User, 'check_password', return_value=False) as mock_check:
                success, message, logged_user = AuthService.login_user(
                    email=email,
                    password="wrongpassword"
                )

                assert success is False
                assert "incorrect" in message
                assert logged_user is None
                mock_find.assert_called_once_with(email)
                mock_check.assert_called_once_with(user.password, "wrongpassword")
                print(f"Login wrong password test passed. Message: {message}")

    def test_logout_user(self, mock_session):
        """Test logging out a user."""
        print_separator("Testing user logout")

        # Set up the session with some data
        mock_session['user_id'] = 'test-user-id'
        mock_session['user_email'] = 'test@example.com'
        mock_session['user_name'] = 'Test User'

        # Call the logout method
        success, message = AuthService.logout_user()

        assert success is True
        assert "réussie" in message
        assert len(mock_session) == 0  # Session should be cleared
        print(f"Logout test passed. Message: {message}")

    def test_is_authenticated_true(self, mock_session):
        """Test is_authenticated when user is logged in."""
        print_separator("Testing is_authenticated - true case")

        # Set up the session with user_id
        mock_session['user_id'] = 'test-user-id'

        # Call the is_authenticated method
        is_auth = AuthService.is_authenticated()

        assert is_auth is True
        print("is_authenticated true test passed.")

    def test_is_authenticated_false(self, mock_session):
        """Test is_authenticated when user is not logged in."""
        print_separator("Testing is_authenticated - false case")

        # Ensure session is empty
        mock_session.clear()

        # Call the is_authenticated method
        is_auth = AuthService.is_authenticated()

        assert is_auth is False
        print("is_authenticated false test passed.")

    def test_get_current_user_id(self, mock_session):
        """Test getting the current user ID from session."""
        print_separator("Testing get_current_user_id")

        # Set up the session with user_id
        test_id = 'test-user-id'
        mock_session['user_id'] = test_id

        # Call the get_current_user_id method
        user_id = AuthService.get_current_user_id()

        assert user_id == test_id
        print(f"get_current_user_id test passed. User ID: {user_id}")

    def test_get_current_user_name(self, mock_session):
        """Test getting the current user name from session."""
        print_separator("Testing get_current_user_name")

        # Set up the session with user_name
        test_name = 'Test User'
        mock_session['user_name'] = test_name

        # Call the get_current_user_name method
        user_name = AuthService.get_current_user_name()

        assert user_name == test_name
        print(f"get_current_user_name test passed. User name: {user_name}")

    def test_integration_register_login_logout(self):
        """Integration test for register, login, and logout workflow."""
        print_separator("Integration test: register -> login -> logout")

        # Generate unique email for this test
        unique_email = f"integration.test.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        password = "integration123"

        # 1. Register a new user - mock for success
        with patch.object(User, 'find_by_email', return_value=None):
            with patch.object(User, 'save', return_value=True):
                reg_success, reg_message = AuthService.register_user(
                    last_name="Integration",
                    first_name="Test",
                    email=unique_email,
                    password=password
                )
                assert reg_success is True
                print(f"1. Registration: {reg_message}")

        # 2. Mock the user for login
        mock_user = MagicMock()
        mock_user.id = str(uuid.uuid4())
        mock_user.email = unique_email
        mock_user.first_name = "Integration"
        mock_user.last_name = "Test"
        mock_user.password = "hashed_password"
        mock_user.is_active = True

        # 3. Login with this user
        mock_session = {}
        with patch.object(User, 'find_by_email', return_value=mock_user):
            with patch.object(User, 'check_password', return_value=True):
                with patch('server.services.auth.session', mock_session):
                    login_success, login_message, user = AuthService.login_user(
                        email=unique_email,
                        password=password
                    )
                    assert login_success is True
                    assert 'user_id' in mock_session
                    print(f"2. Login: {login_message}")

        # 4. Logout
        with patch('server.services.auth.session', mock_session):
            logout_success, logout_message = AuthService.logout_user()
            assert logout_success is True
            assert len(mock_session) == 0
            print(f"3. Logout: {logout_message}")

        print("Integration test completed successfully.")


if __name__ == "__main__":
    pytest.main(["-v", __file__])