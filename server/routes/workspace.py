from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast
from server.database.models import User, Organisation

workspace_bp = Blueprint('workspace', __name__)


@workspace_bp.before_request
def check_auth():
    """Ensure user is authenticated before accessing workspace pages"""
    if not AuthService.is_authenticated():
        set_toast('Veuillez vous connecter pour accéder à cette page.', 'error')
        return redirect(url_for('auth.auth_page'))


def is_admin_or_super_admin(org_id):
    """Check if current user is an admin or super admin of the organization"""
    user_id = AuthService.get_current_user_id()

    # Get the organization
    org = Organisation.find_by_id(org_id)

    # Check if the user is the super admin
    if org and str(org.super_admin_id) == user_id:
        return True

    # Check if the user has admin role in this organization
    is_admin = Organisation.check_user_role(org_id, user_id, 'Administrateur')

    return is_admin


@workspace_bp.route('/projects')
def projects():
    """My projects page"""
    user_id = AuthService.get_current_user_id()
    # Get projects for this user (placeholder data for now)
    # Using dummy data until Project model is implemented
    projects = [
        {
            'id': '1',
            'nom': 'Projet de démonstration',
            'numero': 'PRJ-2025-001',
            'description': 'Un projet de démonstration pour tester l\'interface.',
            'started_at': '2025-03-01',
            'status': 'active',
            'type': 'Démonstration'
        }
    ]

    return render_template('workspace/projects.html', projects=projects)


@workspace_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create new project page"""
    if request.method == 'POST':
        # Process the form submission here
        # For now, redirect back to projects page with a success message
        set_toast('Projet créé avec succès!', 'success')
        return redirect(url_for('workspace.projects'))

    # Dummy organization data for form
    organisations = [
        {'id': '1', 'nom': 'GLO-2005'}
    ]

    return render_template('workspace/new_project.html', organisations=organisations)


@workspace_bp.route('/projects/<project_id>')
def project_detail(project_id):
    """Project detail page"""
    # Get the project details (dummy data for now)
    project = {
        'id': project_id,
        'nom': 'Projet de démonstration',
        'numero': 'PRJ-2025-001',
        'description': 'Un projet de démonstration pour tester l\'interface.',
        'started_at': '2025-03-01',
        'status': 'active',
        'type': 'Démonstration'
    }

    return render_template('workspace/project_detail.html', project=project)


@workspace_bp.route('/organisations')
def organisations():
    """Organizations page"""
    user_id = AuthService.get_current_user_id()
    # Get organizations for this user (placeholder data for now)
    organisations = [
        {
            'id': '1',
            'nom': 'GLO-2005',
            'members': [{'id': '1', 'name': 'Sébastien Gagnon'}],
            'projects': [{'id': '1', 'name': 'Projet de démonstration'}]
        }
    ]

    return render_template('workspace/organisations.html', organisations=organisations)


@workspace_bp.route('/organisations/new', methods=['GET', 'POST'])
def new_organisation():
    """Create new organization page"""
    if request.method == 'POST':
        # Process the form submission here
        # For now, redirect back to organizations page with a success message
        set_toast('Organisation créée avec succès!', 'success')
        return redirect(url_for('workspace.organisations'))

    return render_template('workspace/new_organisation.html')


@workspace_bp.route('/organisations/<org_id>')
def organisation_detail(org_id):
    """Organization detail page"""
    # Get the organization
    organisation = Organisation.find_by_id(org_id)

    if not organisation:
        abort(404)

    # Check if the user is an admin or super admin
    is_admin = is_admin_or_super_admin(org_id)

    # Get all members in the organization
    members = Organisation.get_users_with_roles(org_id)

    # Get all projects in the organization (dummy data for now)
    projects = [{'id': '1', 'name': 'Projet de démonstration'}]

    return render_template(
        'workspace/organisation_detail.html',
        organisation=organisation,
        members=members,
        projects=projects,
        is_admin_or_super_admin=is_admin
    )


@workspace_bp.route('/organisations/<org_id>/users')
def organisation_users(org_id):
    """Organization users management page - Only accessible to admins and super admins"""
    # Check if the user has admin access
    if not is_admin_or_super_admin(org_id):
        set_toast('Vous n\'avez pas les permissions nécessaires pour accéder à cette page.', 'error')
        return redirect(url_for('workspace.organisations'))

    # Get the organization
    organisation = Organisation.find_by_id(org_id)

    if not organisation:
        abort(404)

    # Get all users in the organization with their roles
    users = Organisation.get_users_with_roles(org_id)

    # Get all available roles for this organization
    roles = Organisation.get_available_roles(org_id)

    return render_template(
        'workspace/organisation_users.html',
        organisation=organisation,
        users=users,
        roles=roles
    )


@workspace_bp.route('/organisations/<org_id>/users/update', methods=['POST'])
def update_user_role(org_id):
    """Update a user's role within an organization - Only accessible to admins and super admins"""
    # Check if the user has admin access
    if not is_admin_or_super_admin(org_id):
        return {'success': False, 'message': 'Permission denied'}, 403

    data = request.json
    user_id = data.get('user_id')
    role_id = data.get('role_id')
    company = data.get('company')
    location = data.get('location')

    # Update the user's role and info
    success = Organisation.update_user_info(org_id, user_id, role_id, company, location)

    if success:
        return {'success': True, 'message': 'Informations mises à jour avec succès'}
    else:
        return {'success': False, 'message': 'Une erreur est survenue lors de la mise à jour'}, 500