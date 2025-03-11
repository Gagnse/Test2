from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast
from server.database.models import Project
from server.database.models import Organizations

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
        print(f"Processing project: {project.id} - {project.name}")  # Debugging
        projects.append({
            'id': project.id,
            'name': project.name,
            'project_number': project.project_number,
            'description': project.description,
            'start_date': project.start_date,
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
        project_number = request.form.get('project_number')
        name = request.form.get('name')
        description = request.form.get('description')
        organisation_id = request.form.get('organisation_id')

        print(f"Debug: Données reçues pour la création du projet: {data}")

        # Create new project
        project = Project(
            project_number=project_number,
            name=name,
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
    user_organizations = Organizations.find_by_user(user_id)
    organizations = []
    for org in user_organizations:
        organizations.append({
            'id': org.id,
            'name': org.name
        })

    return render_template('workspace/new_project.html', organizations=organizations)


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
        'name': project_obj.name,
        'project_number': project_obj.project_number,
        'description': project_obj.description,
        'start_date': project_obj.start_date,
        'status': project_obj.status or 'Unknown',
        'type': project_obj.type or 'N/A'
    }

    return render_template('workspace/project_detail.html', project=project)


@workspace_bp.route('/organisations')
def organisations():
    """Organizations page for current user"""
    user_id = AuthService.get_current_user_id()
    print(f"Current user ID: {user_id}")

    # Get the first organization for this user
    # Since a user belongs to only one organization
    user_organizations = Organizations.find_by_user(user_id)

    if not user_organizations:
        set_toast('Vous n\'êtes pas membre d\'une organisation.', 'error')
        return redirect(url_for('home'))

    # Get the first (and only) organization
    org = user_organizations[0]
    print(f"Found organization: {org.name} (ID: {org.id})")

    # Ensure the current user is included by directly adding them if needed
    members_list = []

    # Get all users
    users = org.get_users()
    print(f"Retrieved {len(users)} members from get_users()")

    if not users:
        # If no users were returned, there may be an issue with the relationship
        # At the very least, add the current user
        current_user = Users.find_by_id(user_id)
        if current_user:
            print(f"Adding current user {current_user.first_name} {current_user.last_name} to members list")
            members_list.append({
                'id': current_user.id,
                'last_name': current_user.last_name,
                'first_name': current_user.first_name,
                'email': current_user.email,
                'created_at': current_user.created_at,
                'is_active': current_user.is_active,
                'role': 'Administrateur'  # Assume admin role for current user
            })
    else:
        # Process all retrieved users
        for member in users:
            # Get the roles for this member in this organization
            roles = org.get_user_roles(member.id) if hasattr(org, 'get_user_roles') else []
            role_name = roles[0]['nom'] if roles else 'Membre'

            members_list.append({
                'id': member.id,
                'last_name': member.last_name,
                'first_name': member.first_name,
                'email': member.email,
                'created_at': member.created_at,
                'is_active': member.is_active,
                'role': role_name
            })

    # Get projects for this organization
    project_list = []
    projects = org.get_projects()
    print(f"Retrieved {len(projects)} projects")

    for proj in projects:
        project_list.append({
            'id': proj.id,
            'project_number': proj.project_number,
            'name': proj.name,
            'description': proj.description,
            'start_date': proj.start_date,
            'end_date': proj.end_date,
            'status': proj.status or 'Actif',
            'type': proj.type or 'Divers'
        })

    # Get roles for this organization
    roles_list = org.get_roles()
    print(f"Retrieved {len(roles_list)} roles")

    # Create the organization data structure
    organization = {
        'id': org.id,
        'name': org.name,
        'created_at': org.created_at,
        'super_admin_id': org.super_admin_id,
        'members': members_list,
        'projects': project_list,
        'roles': roles_list
    }

    return render_template('workspace/organisations.html', organisation=organisation)


@workspace_bp.route('/organisations/<org_id>')
def organisation_detail(org_id):
    """Organization detail page"""
    # Get the organization details using the Organisation model
    org = Organizations.find_by_id(org_id)

    if not org:
        set_toast('Organisation non trouvée.', 'error')
        return redirect(url_for('workspace.organisations'))

    # Get members and projects for this organization
    members = org.get_users()
    projects = org.get_projects()

    member_list = [{'id': member.id, 'name': f"{member.first_name} {member.last_name}"} for member in members]
    project_list = [{'id': proj.id, 'name': proj.name} for proj in projects]

    organisation = {
        'id': org.id,
        'name': org.name,
        'members': member_list,
        'projects': project_list
    }

    return render_template('workspace/organisation_detail.html', organisation=organisation)