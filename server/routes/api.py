from flask import Blueprint, request, jsonify, session
from server.services.auth import AuthService
from server.database.models import User, Project, Organizations
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
        data['last_name'],
        data['first_name'],
        data['email'],
        data['password']
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
        projects.append({
            'id': project.id,
            'name': project.name,
            'project_number': project.project_number,
            'description': project.description,
            'started_at': project.started_at.isoformat() if project.started_at else None,
            'ended_at': project.ended_at.isoformat() if project.ended_at else None,
            'status': project.status,
            'type': project.type
        })

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

    # Get the user's organization ID using a method from the User class
    from server.database.models import User

    # This would be a new method you'd add to the User class
    organization_id = User.get_user_org_id(user_id)

    try:
        project = Project(
            project_number=data['project_number'],
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'Actif'),
            type=data.get('type', 'Divers'),
            organization_id=organization_id  # Set the organization ID here
        )

        if project.save():
            project.add_user(user_id)
            return jsonify({
                'success': True,
                'message': 'Projet créé avec succès',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'project_number': project.project_number,
                    'organization_id': organization_id
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
        'started_at': project.started_at.isoformat() if project.started_at else None,
        'ended_at': project.ended_at.isoformat() if project.ended_at else None,
        'status': project.status,
        'type': project.type
    }

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
    user_organisations = Organisation.find_by_user(user_id)

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
