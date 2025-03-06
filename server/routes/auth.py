from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth', methods=['GET'])
def auth_page():
    """Render the authentication widget page"""
    return render_template('auth/auth_widget.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    # Get form data
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Basic validation
    if not all([nom, prenom, email, password, confirm_password]):
        return redirect(redirect_with_toast(
            url_for('auth.auth_page', tab='signup'),
            'Tous les champs sont obligatoires.',
            'error'
        ))

    if password != confirm_password:
        return redirect(redirect_with_toast(
            url_for('auth.auth_page', tab='signup'),
            'Les mots de passe ne correspondent pas.',
            'error'
        ))

    # Register user
    success, message = AuthService.register_user(nom, prenom, email, password)

    if success:
        return redirect(redirect_with_toast(
            url_for('auth.auth_page'),
            message,
            'success'
        ))
    else:
        return redirect(redirect_with_toast(
            url_for('auth.auth_page', tab='signup'),
            message,
            'error'
        ))

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([email, password]):
        return redirect(redirect_with_toast(
            url_for('auth.auth_page'),
            'Veuillez entrer votre email et mot de passe.',
            'error'
        ))

    success, message, user = AuthService.login_user(email, password)

    if success:
        # Set toast in session for the home page
        set_toast(message, 'success')
        return redirect(url_for('home'))
    else:
        return redirect(redirect_with_toast(
            url_for('auth.auth_page'),
            message,
            'error'
        ))

@auth_bp.route('/logout')
def logout():
    success, message = AuthService.logout_user()
    return redirect(redirect_with_toast(
        url_for('home'),
        message,
        'success'
    ))

@auth_bp.route('/profile')
def profile():
    if not AuthService.is_authenticated():
        return redirect(redirect_with_toast(
            url_for('auth.auth_page'),
            'Veuillez vous connecter pour accéder à votre profil.',
            'error'
        ))

    return render_template('auth/profile.html')