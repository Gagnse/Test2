from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast
from server.database.models import User, Organizations, Invitation
import datetime

invitation_bp = Blueprint('invitation', __name__)


@invitation_bp.route('/invitation/accept/<token>')
def accept_invitation(token):
    """Display the invitation acceptance page"""
    # Find invitation by token
    invitation = Invitation.find_by_token(token)

    if not invitation:
        set_toast('Invitation non trouvée. Veuillez contacter l\'administrateur.', 'error')
        return redirect(url_for('home'))

    # Check if invitation is valid
    if not invitation.is_valid():
        if invitation.status == 'accepted':
            set_toast('Cette invitation a déjà été acceptée. Veuillez vous connecter.', 'info')
            return redirect(url_for('auth.login'))
        elif invitation.status == 'cancelled':
            set_toast('Cette invitation a été annulée. Veuillez contacter l\'administrateur.', 'error')
            return redirect(url_for('home'))
        else:  # expired
            set_toast('Cette invitation a expiré. Veuillez contacter l\'administrateur pour une nouvelle invitation.',
                      'error')
            return redirect(url_for('home'))

    # Get organization info
    organization = Organizations.find_by_id(invitation.organization_id)
    if not organization:
        set_toast('Organisation non trouvée. Veuillez contacter l\'administrateur.', 'error')
        return redirect(url_for('home'))

    # Check if user is already logged in
    if AuthService.is_authenticated():
        current_user_id = AuthService.get_current_user_id()
        current_user = User.find_by_id(current_user_id)

        # If the logged-in user is the same as the invited user, redirect to set password
        if current_user and current_user.email == invitation.email:
            # Update invitation status to accepted
            invitation.accept()

            set_toast('Invitation acceptée. Vous êtes maintenant membre de l\'organisation.', 'success')
            return redirect(url_for('workspace.organisations'))

        # Otherwise, ask them to log out first
        set_toast('Vous êtes connecté avec un compte différent. Veuillez vous déconnecter d\'abord.', 'warning')
        return redirect(url_for('auth.logout') + '?next=' + url_for('invitation.accept_invitation', token=token))

    # If we get here, show the invitation acceptance form
    return render_template('auth/accept_invitation.html',
                           invitation=invitation,
                           organization=organization)


@invitation_bp.route('/invitation/complete/<token>', methods=['POST'])
def complete_invitation(token):
    """Process the invitation form submission and create user account"""
    # Find invitation by token
    invitation = Invitation.find_by_token(token)

    if not invitation:
        set_toast('Invitation non trouvée. Veuillez contacter l\'administrateur.', 'error')
        return redirect(url_for('home'))

    # Check if invitation is valid
    if not invitation.is_valid():
        set_toast('Cette invitation n\'est plus valide. Veuillez contacter l\'administrateur.', 'error')
        return redirect(url_for('home'))

    # Get password from form
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Validate password
    if not password or not confirm_password:
        flash('Veuillez entrer un mot de passe.', 'error')
        return redirect(url_for('invitation.accept_invitation', token=token))

    if password != confirm_password:
        flash('Les mots de passe ne correspondent pas.', 'error')
        return redirect(url_for('invitation.accept_invitation', token=token))

    # Create user
    success, message = AuthService.register_user(
        first_name=invitation.first_name,
        last_name=invitation.last_name,
        email=invitation.email,
        password=password,
        organization_id=invitation.organization_id,
        department=invitation.department,
        location=invitation.location,
        role=invitation.role
    )

    if not success:
        flash(message, 'error')
        return redirect(url_for('invitation.accept_invitation', token=token))

    # Update invitation status to accepted
    invitation.accept()

    # Log in the new user
    success, login_message, user = AuthService.login_user(invitation.email, password)

    if not success:
        flash('Votre compte a été créé, mais la connexion automatique a échoué. Veuillez vous connecter.', 'warning')
        return redirect(url_for('auth.login'))

    set_toast('Bienvenue sur SpaceLogic! Votre compte a été créé avec succès.', 'success')
    return redirect(url_for('workspace.organisations'))