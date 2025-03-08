from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast
from server.database.models import Project
from server.database.models import Organisation

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
    print(f"Current user ID: {user_id}")  # Debugging

    # Debug count
    project_count = Project.count_user_projects(user_id)
    print(f"Direct count of projects in database: {project_count}")

    # Get projects for this user using the Project model
    user_projects = Project.find_by_user(user_id)
    print(f"Projects found: {len(user_projects)}")  # Debugging

    # Convert project objects to dictionaries for the template
    projects = []
    for project in user_projects:
        print(f"Processing project: {project.id} - {project.nom}")  # Debugging
        projects.append({
            'id': project.id,
            'nom': project.nom,
            'numero': project.numero,
            'description': project.description,
            'started_at': project.started_at,
            'status': project.status or 'Unknown',
            'type': project.type or 'N/A'
        })

    print(f"Final projects list length: {len(projects)}")  # Debugging
    return render_template('workspace/projects.html', projects=projects)


@workspace_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create new project page"""
    user_id = AuthService.get_current_user_id()

    if request.method == 'POST':
        # Extract form data
        numero = request.form.get('numero')
        nom = request.form.get('nom')
        description = request.form.get('description')
        organisation_id = request.form.get('organisation_id')

        # Create new project
        project = Project(
            numero=numero,
            nom=nom,
            description=description
        )

        # Save the project and add the current user to it
        if project.save():
            project.add_user(user_id)

            # If an organization was selected, associate the project with it
            if organisation_id:
                # You would need to add a method to associate a project with an org
                # This is just a placeholder for the logic
                # e.g., project.set_organisation(organisation_id)
                pass

            set_toast('Projet créé avec succès!', 'success')
            return redirect(url_for('workspace.projects'))
        else:
            set_toast('Erreur lors de la création du projet.', 'error')

    # Get organizations for this user
    user_organisations = Organisation.find_by_user(user_id)
    organisations = []
    for org in user_organisations:
        organisations.append({
            'id': org.id,
            'nom': org.nom
        })

    return render_template('workspace/new_project.html', organisations=organisations)


@workspace_bp.route('/projects/<project_id>')
def project_detail(project_id):
    """Project detail page"""
    # Get the project details using the Project model
    project_obj = Project.find_by_id(project_id)

    if not project_obj:
        set_toast('Projet non trouvé.', 'error')
        return redirect(url_for('workspace.projects'))

    project = {
        'id': project_obj.id,
        'nom': project_obj.nom,
        'numero': project_obj.numero,
        'description': project_obj.description,
        'started_at': project_obj.started_at,
        'status': project_obj.status or 'Unknown',
        'type': project_obj.type or 'N/A'
    }

    return render_template('workspace/project_detail.html', project=project)


@workspace_bp.route('/organisations')
def organisations():
    """Organizations page"""
    user_id = AuthService.get_current_user_id()

    # Get organizations for this user using the Organisation model
    user_organisations = Organisation.find_by_user(user_id)

    organisations = []
    for org in user_organisations:
        # Get members and projects for this organization
        members = org.get_users()
        projects = org.get_projects()

        member_list = [{'id': member.id, 'name': f"{member.prenom} {member.nom}"} for member in members]
        project_list = [{'id': proj.id, 'name': proj.nom} for proj in projects]

        organisations.append({
            'id': org.id,
            'nom': org.nom,
            'members': member_list,
            'projects': project_list
        })

    return render_template('workspace/organisations.html', organisations=organisations)


@workspace_bp.route('/organisations/<org_id>')
def organisation_detail(org_id):
    """Organization detail page"""
    # Get the organization details using the Organisation model
    org = Organisation.find_by_id(org_id)

    if not org:
        set_toast('Organisation non trouvée.', 'error')
        return redirect(url_for('workspace.organisations'))

    # Get members and projects for this organization
    members = org.get_users()
    projects = org.get_projects()

    member_list = [{'id': member.id, 'name': f"{member.prenom} {member.nom}"} for member in members]
    project_list = [{'id': proj.id, 'name': proj.nom} for proj in projects]

    organisation = {
        'id': org.id,
        'nom': org.nom,
        'members': member_list,
        'projects': project_list
    }

    return render_template('workspace/organisation_detail.html', organisation=organisation)