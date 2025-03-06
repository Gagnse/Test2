from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.services.auth import AuthService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic validation
        if not all([nom, prenom, email, password, confirm_password]):
            flash('Tous les champs sont obligatoires.', 'error')
            return render_template('auth/signup.html')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('auth/signup.html')

        # Register user
        success, message = AuthService.register_user(nom, prenom, email, password)

        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')

    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([email, password]):
            flash('Veuillez entrer votre email et mot de passe.', 'error')
            return render_template('auth/login.html')

        success, message, user = AuthService.login_user(email, password)

        if success:
            flash(message, 'success')
            return redirect(url_for('home'))
        else:
            flash(message, 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    success, message = AuthService.logout_user()
    flash(message, 'success')
    return redirect(url_for('home'))


@auth_bp.route('/profile')
def profile():
    if not AuthService.is_authenticated():
        flash('Veuillez vous connecter pour accéder à votre profil.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html')