#!/usr/bin/env python3
"""
Authentication service for user authentication and session management.
"""

from flask import session
from server.database.models import User


class AuthService:
    @staticmethod
    def register_user(nom=None, prenom=None, last_name=None, first_name=None, email=None, password=None,
                      organization_id=None, department=None, location=None, role=None):
        """
        Register a new user
        Returns (success, message)
        """
        # Use either the English or French parameter names
        last_name = last_name or nom
        first_name = first_name or prenom

        if not all([last_name, first_name, email, password]):
            return False, "Tous les champs sont obligatoires."

        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return False, "Un utilisateur avec cet email existe déjà."

        # Create and save new user
        new_user = User(
            last_name=last_name,
            first_name=first_name,
            email=email,
            password=password,  # Will be hashed in the save method
            organization_id=organization_id,
            department=department,
            location=location,
            role=role
        )

        if new_user.save():
            # If organization_id is provided, add the user to the organization
            if organization_id:
                from server.database.models import Organizations
                org = Organizations.find_by_id(organization_id)
                if org:
                    org.add_user(new_user.id)

            return True, "Inscription réussie!"
        else:
            return False, "Une erreur est survenue lors de l'inscription."

    @staticmethod
    def login_user(email, password):
        """
        Authenticate a user
        Returns (success, message, user)
        """
        user = User.find_by_email(email)

        if not user:
            return False, "Email ou mot de passe incorrect.", None

        if hasattr(user, 'is_active') and not user.is_active:
            return False, "Ce compte a été désactivé.", None

        if User.check_password(user.password, password):
            # Set up session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = f"{user.first_name} {user.last_name}"
            return True, "Connexion réussie!", user
        else:
            return False, "Email ou mot de passe incorrect.", None

    @staticmethod
    def logout_user():
        """Log out the current user by clearing session data"""
        session.clear()
        return True, "Déconnexion réussie!"

    @staticmethod
    def is_authenticated():
        """Check if user is logged in"""
        return 'user_id' in session

    @staticmethod
    def get_current_user_id():
        """Get the current user's ID from session"""
        return session.get('user_id')

    @staticmethod
    def get_current_user_name():
        """Get the current user's name from session"""
        return session.get('user_name')