from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast
from server.database.models import User

workspace_bp = Blueprint('workspace', __name__)


@workspace_bp.before_request
def check_auth():
    """Ensure user is authenticated before accessing workspace pages"""
    if not AuthService.is_authenticated():
        set_toast('Veuillez vous connecter pour accéder à cette page.', 'error')
        return redirect(url_for('auth.auth_page'))


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
    # Get the organization details (dummy data for now)
    organisation = {
        'id': org_id,
        'nom': 'GLO-2005',
        'members': [{'id': '1', 'name': 'Sébastien Gagnon'}],
        'projects': [{'id': '1', 'name': 'Projet de démonstration'}]
    }

    return render_template('workspace/organisation_detail.html', organisation=organisation)