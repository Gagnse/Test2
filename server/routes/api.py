from flask import Blueprint, request, jsonify, session
from server.services.auth import AuthService
from server.database.models import User, Project, Organizations
from server.database.db_config import get_db_connection, close_connection
import json

api_bp = Blueprint('api', __name__)


# Authentication endpoints
@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    success, message, user = AuthService.login_user(data['email'], data['password'])

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}"
            }
        })
    else:
        return jsonify({'success': False, 'message': message}), 401


@api_bp.route('/auth/signup', methods=['POST'])
def api_signup():
    """API endpoint for user signup"""
    data = request.get_json()

    if not data or not all(k in data for k in ('last_name', 'first_name', 'email', 'password')):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    success, message = AuthService.register_user(
        last_name=data['last_name'],
        first_name=data['first_name'],
        email=data['email'],
        password=data['password']
    )

    if success:
        return jsonify({'success': True, 'message': message}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400


@api_bp.route('/auth/logout', methods=['POST'])
def api_logout():
    """API endpoint for user logout"""
    success, message = AuthService.logout_user()
    return jsonify({'success': success, 'message': message})


@api_bp.route('/auth/status', methods=['GET'])
def api_auth_status():
    """Check if user is authenticated"""
    is_authenticated = AuthService.is_authenticated()
    data = {
        'authenticated': is_authenticated
    }

    if is_authenticated:
        data['user'] = {
            'id': session.get('user_id'),
            'email': session.get('user_email'),
            'name': session.get('user_name')
        }

    return jsonify(data)


# Project endpoints
@api_bp.route('/projects', methods=['GET'])
def api_get_projects():
    """Get all projects for the authenticated user"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    user_id = AuthService.get_current_user_id()
    user_projects = Project.find_by_user(user_id)

    projects = []
    for project in user_projects:
        project_data = {
            'id': project.id,
            'name': project.name,
            'project_number': project.project_number,
            'description': project.description,
        }

        # Add optional fields if they exist
        if hasattr(project, 'start_date') and project.start_date:
            project_data['start_date'] = project.start_date.isoformat()
        if hasattr(project, 'end_date') and project.end_date:
            project_data['end_date'] = project.end_date.isoformat()
        if hasattr(project, 'status'):
            project_data['status'] = project.status
        if hasattr(project, 'type'):
            project_data['type'] = project.type

        projects.append(project_data)

    return jsonify({'success': True, 'projects': projects})


@api_bp.route('/projects', methods=['POST'])
def api_create_project():
    """Create a new project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    data = request.get_json()

    if not data or not all(k in data for k in ('project_number', 'name')):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    user_id = AuthService.get_current_user_id()

    # Get the user's organization ID
    organization_id = User.get_user_org_id(user_id)

    if not organization_id:
        return jsonify({'success': False, 'message': 'User is not associated with any organization'}), 400

    try:
        # Sanitize project number (remove spaces, special characters) for database name
        sanitized_number = ''.join(c for c in data['project_number'] if c.isalnum() or c in '-_')

        # Check if project number already exists
        connection = get_db_connection('users_db')
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects WHERE project_number = %s", (sanitized_number,))
            result = cursor.fetchone()

            if result and result[0] > 0:
                return jsonify({
                    'success': False,
                    'message': 'Un projet avec ce numéro existe déjà. Veuillez utiliser un numéro unique.'
                }), 400
        finally:
            close_connection(connection, cursor)

        project = Project(
            project_number=sanitized_number,
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'Actif'),
            type=data.get('type', 'Divers'),
            organization_id=organization_id
        )

        if project.save():
            # Add the user to the project
            project.add_user(user_id)

            return jsonify({
                'success': True,
                'message': 'Projet créé avec succès',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'project_number': project.project_number,
                    'organization_id': organization_id,
                    'database_name': f"SPACELOGIC_{sanitized_number.replace('-', '_')}"
                }
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Erreur lors de la création du projet'}), 500
    except Exception as e:
        import traceback
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Error creating project: {error_message}")
        print(f"Traceback: {error_traceback}")

        # Check for duplicate key error
        if "Duplicate entry" in error_message and "project_number" in error_message:
            return jsonify({
                'success': False,
                'message': 'Un projet avec ce numéro existe déjà. Veuillez utiliser un numéro unique.'
            }), 400

        return jsonify({
            'success': False,
            'message': f"Erreur lors de la création du projet: {error_message}",
            'error_type': type(e).__name__
        }), 500


@api_bp.route('/projects/<project_id>', methods=['GET'])
def api_get_project(project_id):
    """Get a specific project by ID"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    project = Project.find_by_id(project_id)

    if not project:
        return jsonify({'success': False, 'message': 'Projet non trouvé'}), 404

    project_data = {
        'id': project.id,
        'name': project.name,
        'project_number': project.project_number,
        'description': project.description,
    }

    # Add optional fields if they exist
    if hasattr(project, 'start_date') and project.start_date:
        project_data['start_date'] = project.start_date.isoformat()
    if hasattr(project, 'end_date') and project.end_date:
        project_data['end_date'] = project.end_date.isoformat()
    if hasattr(project, 'status'):
        project_data['status'] = project.status
    if hasattr(project, 'type'):
        project_data['type'] = project.type

    return jsonify({'success': True, 'project': project_data})


@api_bp.route('/projects/<project_id>', methods=['PUT'])
def api_update_project(project_id):
    """Update a specific project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    project = Project.find_by_id(project_id)

    if not project:
        return jsonify({'success': False, 'message': 'Projet non trouvé'}), 404

    data = request.get_json()

    if 'name' in data:
        project.name = data['name']
    if 'project_number' in data:
        project.project_number = data['project_number']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    if 'type' in data:
        project.type = data['type']

    if project.save():
        return jsonify({'success': True, 'message': 'Projet mis à jour avec succès'})
    else:
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour du projet'}), 500


@api_bp.route('/projects/<project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    """Delete a specific project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    # This would require adding a delete method to the Project model
    # For now, we'll return a placeholder response
    return jsonify({'success': False, 'message': 'Fonctionnalité non implémentée'}), 501


# Organisation endpoints
@api_bp.route('/organisations', methods=['GET'])
def api_get_organisations():
    """Get all organisations for the authenticated user"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    user_id = AuthService.get_current_user_id()
    user_organisations = Organizations.find_by_user(user_id)

    organisations = []
    for org in user_organisations:
        # Get members count (we'd need to add this method to the model)
        members_count = len(org.get_users()) if hasattr(org, 'get_users') else 0
        # Get projects count (we'd need to add this method to the model)
        projects_count = len(org.get_projects()) if hasattr(org, 'get_projects') else 0

        organisations.append({
            'id': org.id,
            'name': org.name,
            'created_at': org.created_at.isoformat() if org.created_at else None,
            'members_count': members_count,
            'projects_count': projects_count
        })

    return jsonify({'success': True, 'organisations': organisations})


@api_bp.route('/organisations/<org_id>', methods=['GET'])
def api_get_organisation(org_id):
    """Get a specific organisation by ID"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    org = Organizations.find_by_id(org_id)

    if not org:
        return jsonify({'success': False, 'message': 'Organisation non trouvée'}), 404

    # Get members and projects if these methods exist
    members = []
    if hasattr(org, 'get_users'):
        user_list = org.get_users()
        for user in user_list:
            members.append({
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'is_admin': user.id == org.super_admin_id
            })

    projects = []
    if hasattr(org, 'get_projects'):
        project_list = org.get_projects()
        for project in project_list:
            projects.append({
                'id': project.id,
                'name': project.name,
                'project_number': project.project_number,
                'status': project.status if hasattr(project, 'status') else 'Unknown'
            })

    roles = []
    if hasattr(org, 'get_roles'):
        roles = org.get_roles()

    organisation_data = {
        'id': org.id,
        'name': org.name,
        'created_at': org.created_at.isoformat() if org.created_at else None,
        'super_admin_id': org.super_admin_id,
        'members': members,
        'projects': projects,
        'roles': roles
    }

    return jsonify({'success': True, 'organisation': organisation_data})


@api_bp.route('/organisations', methods=['POST'])
def api_create_organisation():
    """Create a new organisation"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Le nom de l\'organisation est requis'}), 400

    user_id = AuthService.get_current_user_id()

    org = Organizations(
        name=data['name'],
        super_admin_id=user_id
    )

    if org.save():
        # Add the user to the organization
        if hasattr(org, 'add_user'):
            org.add_user(user_id)

        return jsonify({
            'success': True,
            'message': 'Organisation créée avec succès',
            'organisation': {
                'id': org.id,
                'name': org.name
            }
        }), 201
    else:
        return jsonify({'success': False, 'message': 'Erreur lors de la création de l\'organisation'}), 500