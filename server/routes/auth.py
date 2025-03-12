from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth', methods=['GET'])
def auth_page():
    """Render the authentication widget page"""
    # If already logged in, redirect to workspace
    if AuthService.is_authenticated():
        return redirect(url_for('workspace.projects'))
    return render_template('auth/auth_widget.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup"""
    # GET request: show signup page
    if request.method == 'GET':
        # If already logged in, redirect to workspace
        if AuthService.is_authenticated():
            return redirect(url_for('workspace.projects'))
        return render_template('auth/signup.html')

    # POST request: process signup form
    # Get form data
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Basic validation
    if not all([last_name, first_name, email, password, confirm_password]):
        flash('Tous les champs sont obligatoires.', 'error')
        return redirect(url_for('auth.signup'))

    if password != confirm_password:
        flash('Les mots de passe ne correspondent pas.', 'error')
        return redirect(url_for('auth.signup'))

    # Register user - now using last_name/first_name parameters to match AuthService
    success, message = AuthService.register_user(
        last_name=last_name,
        first_name=first_name,
        email=email,
        password=password
    )

    if success:
        flash(message, 'success')
        return redirect(url_for('auth.login'))
    else:
        flash(message, 'error')
        return redirect(url_for('auth.signup'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # GET request: show login page
    if request.method == 'GET':
        # If already logged in, redirect to workspace
        if AuthService.is_authenticated():
            return redirect(url_for('workspace.projects'))
        return render_template('auth/login.html')

    # POST request: process login form
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([email, password]):
        flash('Veuillez entrer votre email et mot de passe.', 'error')
        return redirect(url_for('auth.login'))

    success, message, user = AuthService.login_user(email, password)

    if success:
        # Set success toast message
        set_toast(message, 'success')
        # Redirect to workspace dashboard
        return redirect(url_for('workspace.projects'))
    else:
        flash(message, 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """Log out user"""
    success, message = AuthService.logout_user()
    # Redirect to home page with toast message
    return redirect(redirect_with_toast(
        url_for('home'),
        message,
        'success'
    ))


@auth_bp.route('/profile')
def profile():
    """User profile page"""
    if not AuthService.is_authenticated():
        flash('Veuillez vous connecter pour accéder à votre profil.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html')