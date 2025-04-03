from flask import Blueprint, request, jsonify, session
from server.services.auth import AuthService
from server.database.models import User, Project, Organizations, Invitation
from server.database.db_config import get_db_connection, close_connection
from server.utils.email_sender import email_sender
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
        # Sanitize project number (remove spaces, special characters) for display purposes
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

        # Create the project object
        project = Project(
            project_number=sanitized_number,
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'Actif'),
            type=data.get('type', 'Divers'),
            organization_id=organization_id
        )

        # Save the project to database
        if project.save():
            # Add the user to the project
            project.add_user(user_id)

            # Ensure we have a valid project.id
            if not project.id:
                # This shouldn't normally happen, but add a safeguard
                return jsonify({'success': False, 'message': 'Error getting project ID after save'}), 500

            # Format UUID without hyphens for database name (handle potential errors)
            try:
                formatted_uuid = project.id.replace('-', '')
                db_name = f"SPACELOGIC_{formatted_uuid}"
            except (AttributeError, TypeError) as e:
                # If there's an issue formatting the UUID, use a fallback
                print(f"Error formatting project UUID: {e}")
                db_name = f"SPACELOGIC_project_{sanitized_number}"

            # Return the result with proper project info
            return jsonify({
                'success': True,
                'message': 'Projet créé avec succès',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'project_number': project.project_number,
                    'organization_id': organization_id,
                    'database_name': db_name
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


@api_bp.route('/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    """Get a specific user by ID"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    user = User.find_by_id(user_id)

    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

    # Get the user's organization
    org_id = user.organization_id
    organization = Organizations.find_by_id(org_id) if org_id else None

    # Get roles for this user in the organization
    roles = []
    if organization:
        # First check if the user is the super_admin
        if user.id == organization.super_admin_id:
            roles = [{'id': 'super-admin', 'name': 'Administrateur', 'description': 'Super Administrator'}]
        else:
            # Get roles from regular assignments
            roles = organization.get_user_roles(user.id)

    # If roles is still empty, add some default roles
    if not roles:
        default_roles = [
            {'id': 'admin', 'name': 'Administrateur', 'description': 'Administrator'},
            {'id': 'collab', 'name': 'Collaborateur', 'description': 'Collaborator'},
            {'id': 'client', 'name': 'Client', 'description': 'Client'},
            {'id': 'member', 'name': 'Membre', 'description': 'Member'}
        ]
        roles = default_roles

    # Make sure we include all relevant fields
    user_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_active': user.last_active.isoformat() if hasattr(user, 'last_active') and user.last_active else None,
        'is_active': user.is_active,
        'department': user.department,
        'location': user.location,
        'role': user.role
    }

    # Add debugging to verify data is being sent correctly
    print(f"Sending user data to client: department={user.department}, location={user.location}, role={user.role}")

    return jsonify({
        'success': True,
        'user': user_data,
        'roles': roles
    })

@api_bp.route('/users/<user_id>', methods=['PUT'])
def api_update_user(user_id):
    """Update a specific user"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    current_user_id = AuthService.get_current_user_id()

    # Get the user to update
    user = User.find_by_id(user_id)

    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

    # Check if the current user has permission to update this user
    # Only allow if it's the same user or the user is an admin of the organization
    org = Organizations.find_by_id(user.organization_id)
    if user_id != current_user_id and (not org or org.super_admin_id != current_user_id):
        return jsonify(
            {'success': False, 'message': 'Vous n\'avez pas la permission de modifier cet utilisateur'}), 403

    data = request.get_json()

    # Update fields that were provided
    if 'department' in data:
        user.department = data['department']
    if 'location' in data:
        user.location = data['location']
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']

    # Save the user
    if user.save():
        return jsonify({'success': True, 'message': 'Utilisateur mis à jour avec succès'})
    else:
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour de l\'utilisateur'}), 500


@api_bp.route('/organisations/<org_id>/users/<user_id>', methods=['DELETE'])
def api_remove_user_from_org(org_id, user_id):
    """Remove a user from an organization"""
    print(f"API request to remove user {user_id} from organization {org_id}")

    if not AuthService.is_authenticated():
        print("Authentication required")
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    current_user_id = AuthService.get_current_user_id()
    print(f"Request made by user: {current_user_id}")

    # Get the organization
    org = Organizations.find_by_id(org_id)

    if not org:
        print(f"Organization {org_id} not found")
        return jsonify({'success': False, 'message': 'Organisation non trouvée'}), 404

    # Check if the current user has permission to remove users
    # Only allow if the current user is the super admin of the organization
    if org.super_admin_id != current_user_id:
        print(f"Permission denied: current user {current_user_id} is not the super admin {org.super_admin_id}")
        return jsonify(
            {'success': False, 'message': 'Permission denied - only organization administrators can remove users'}), 403

    # Prevent removing the super admin (organization owner)
    if user_id == org.super_admin_id:
        print("Cannot remove super admin from organization")
        return jsonify(
            {'success': False, 'message': 'Le super administrateur ne peut pas être supprimé de l\'organisation'}), 400

    # Remove the user from the organization
    print(f"Attempting to remove user {user_id} from organization {org_id}")
    success = org.remove_user(user_id)

    if success:
        print(f"Successfully removed user {user_id} from organization {org_id}")
        return jsonify({
            'success': True,
            'message': 'Utilisateur supprimé de l\'organisation avec succès'
        })
    else:
        print(f"Error removing user {user_id} from organization {org_id}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la suppression de l\'utilisateur'
        }), 500


@api_bp.route('/invitations', methods=['POST'])
def api_create_invitation():
    """Create a new invitation"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    data = request.get_json()

    # Validate required fields
    if not data or not all(k in data for k in ('email', 'first_name', 'last_name', 'role', 'organisation_id')):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Get current user as inviter
    current_user_id = AuthService.get_current_user_id()

    # Check if user has permission to invite to this organization
    # Get their organization ID
    user_org_id = User.get_user_org_id(current_user_id)

    # Check if the organization ID from the request matches the user's organization
    if user_org_id != data['organisation_id']:
        return jsonify({
            'success': False,
            'message': 'Vous n\'avez pas la permission d\'inviter des utilisateurs à cette organisation'
        }), 403

    # Check if the user is a super admin of the organization
    organization = Organizations.find_by_id(user_org_id)
    if not organization or organization.super_admin_id != current_user_id:
        # Could be more specific here and check roles, but for now only super_admin
        return jsonify({
            'success': False,
            'message': 'Seul l\'administrateur de l\'organisation peut envoyer des invitations'
        }), 403

    # Check if there's already a pending invitation for this email in this organization
    existing_invitation = Invitation.find_by_email_and_org(data['email'], data['organisation_id'])
    if existing_invitation:
        return jsonify({
            'success': False,
            'message': 'Une invitation est déjà en cours pour cet email. Veuillez attendre qu\'elle soit acceptée ou annulée.'
        }), 400

    # Check if a user with this email already exists
    existing_user = User.find_by_email(data['email'])
    if existing_user:
        return jsonify({
            'success': False,
            'message': 'Un utilisateur avec cet email existe déjà. Veuillez utiliser une autre adresse email.'
        }), 400

    # Create invitation object but don't save to database yet
    temp_invitation = Invitation(
        organization_id=data['organisation_id'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role'],
        department=data.get('department'),
        location=data.get('location'),
        invited_by=current_user_id
    )

    # Add organization name to the invitation object for the email
    temp_invitation.organization_name = organization.name

    # Send invitation email BEFORE saving to database
    custom_message = data.get('message')
    base_url = request.host_url.rstrip('/')

    # Try to send invitation email with proper error handling
    try:
        email_success = email_sender.send_invitation_email(temp_invitation, base_url, custom_message)

        if not email_success:
            # If email fails, don't create the invitation record
            return jsonify({
                'success': False,
                'message': 'L\'email d\'invitation n\'a pas pu être envoyé. Veuillez vérifier l\'adresse email ou votre configuration SMTP.'
            }), 500
    except Exception as e:
        print(f"Error sending email: {e}")
        # Log the full error details for debugging
        import traceback
        traceback.print_exc()

        # Return an error and don't save the invitation
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'envoi de l\'email: {str(e)}'
        }), 500

    # Only save the invitation to the database if the email was sent successfully
    if temp_invitation.save():
        # Success!
        return jsonify({
            'success': True,
            'message': 'Invitation envoyée avec succès',
            'invitation': {
                'id': temp_invitation.id,
                'email': temp_invitation.email,
                'expires_at': temp_invitation.expires_at.isoformat()
            }
        })
    else:
        # Failed to save to database (unlikely at this point, but still possible)
        return jsonify({
            'success': False,
            'message': 'L\'email a été envoyé mais l\'invitation n\'a pas pu être enregistrée dans la base de données.'
        }), 500


@api_bp.route('/invitations/<invitation_id>', methods=['DELETE'])
def api_cancel_invitation(invitation_id):
    """Cancel an invitation"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    # Get current user as inviter
    current_user_id = AuthService.get_current_user_id()

    # Find the invitation
    connection = get_db_connection('users_db')
    cursor = None
    invitation = None

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT BIN_TO_UUID(id) as id, BIN_TO_UUID(organization_id) as organization_id,
            BIN_TO_UUID(invited_by) as invited_by
            FROM organization_invitations
            WHERE id = UUID_TO_BIN(%s) AND status = 'pending'
        """
        cursor.execute(query, (invitation_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'success': False, 'message': 'Invitation not found or not pending'}), 404

        invitation = {
            'id': result['id'],
            'organization_id': result['organization_id'],
            'invited_by': result['invited_by']
        }
    except Exception as e:
        print(f"Error finding invitation: {e}")
        return jsonify({'success': False, 'message': 'Error retrieving invitation'}), 500
    finally:
        close_connection(connection, cursor)

    # Check if user is allowed to cancel this invitation
    # Either they are the one who invited the user or they are the super admin
    if invitation['invited_by'] != current_user_id:
        # Check if they are super admin
        organization = Organizations.find_by_id(invitation['organization_id'])
        if not organization or organization.super_admin_id != current_user_id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to cancel this invitation'
            }), 403

    # Cancel the invitation
    connection = get_db_connection('users_db')
    cursor = None

    try:
        cursor = connection.cursor()
        query = """
            UPDATE organization_invitations
            SET status = 'cancelled'
            WHERE id = UUID_TO_BIN(%s)
        """
        cursor.execute(query, (invitation_id,))
        connection.commit()

        return jsonify({
            'success': True,
            'message': 'Invitation cancelled successfully'
        })
    except Exception as e:
        print(f"Error cancelling invitation: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Error cancelling invitation'}), 500
    finally:
        close_connection(connection, cursor)


@api_bp.route('/organizations/<org_id>/invitations', methods=['GET'])
def api_get_organization_invitations(org_id):
    """Get all pending invitations for an organization"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    # Get current user as inviter
    current_user_id = AuthService.get_current_user_id()

    # Check if user has permission to view this organization's invitations
    # Get their organization ID
    user_org_id = User.get_user_org_id(current_user_id)

    # Check if the organization ID from the request matches the user's organization
    if user_org_id != org_id:
        return jsonify({
            'success': False,
            'message': 'You do not have permission to view invitations for this organization'
        }), 403

    # Get all pending invitations
    invitations = Invitation.get_pending_invitations_for_organization(org_id)

    # Format the invitations for JSON response
    invitations_data = []
    for invitation in invitations:
        invitations_data.append({
            'id': invitation.id,
            'email': invitation.email,
            'first_name': invitation.first_name,
            'last_name': invitation.last_name,
            'role': invitation.role,
            'department': invitation.department,
            'location': invitation.location,
            'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
            'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
            'invited_by': invitation.invited_by
        })

    return jsonify({
        'success': True,
        'invitations': invitations_data
    })


@api_bp.route('/projects/<project_id>/members', methods=['GET'])
def api_get_project_members(project_id):
    """API endpoint to get all members of a project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    connection = get_db_connection('users_db')
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # Check if the project exists
        cursor.execute("SELECT COUNT(*) as count FROM projects WHERE id = UUID_TO_BIN(%s)", (project_id,))
        result = cursor.fetchone()
        if not result or result['count'] == 0:
            return jsonify({'success': False, 'message': 'Project not found'}), 404

        # Get project members
        query = """
            SELECT 
                BIN_TO_UUID(u.id) as id, 
                u.first_name, 
                u.last_name, 
                u.email,
                u.role,
                u.department, 
                u.location, 
                pu.joined_at
            FROM users u
            JOIN project_users pu ON u.id = pu.user_id
            WHERE pu.project_id = UUID_TO_BIN(%s)
        """
        cursor.execute(query, (project_id,))
        members = cursor.fetchall()

        # Process datetime objects for JSON serialization
        for member in members:
            if 'joined_at' in member and member['joined_at']:
                member['joined_at'] = member['joined_at'].isoformat()

        return jsonify({
            'success': True,
            'members': members
        })

    except Exception as e:
        print(f"Error fetching project members: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@api_bp.route('/projects/<project_id>/available-users', methods=['GET'])
def api_get_available_users(project_id):
    """API endpoint to get users available to add to a project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    connection = get_db_connection('users_db')
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        # First get the organization ID for this project
        query = "SELECT BIN_TO_UUID(organization_id) as organization_id FROM projects WHERE id = UUID_TO_BIN(%s)"
        cursor.execute(query, (project_id,))
        org_result = cursor.fetchone()

        if not org_result:
            return jsonify({'success': False, 'message': 'Project not found'}), 404

        org_id = org_result['organization_id']

        # Get users in this organization who are not already in the project
        query = """
            SELECT 
                BIN_TO_UUID(u.id) as id, 
                u.first_name, 
                u.last_name, 
                u.email
            FROM users u
            JOIN organization_user ou ON u.id = ou.users_id
            WHERE ou.organizations_id = UUID_TO_BIN(%s)
            AND u.id NOT IN (
                SELECT user_id 
                FROM project_users 
                WHERE project_id = UUID_TO_BIN(%s)
            )
            AND u.is_active = 1
        """
        cursor.execute(query, (org_id, project_id))
        users = cursor.fetchall()

        return jsonify({
            'success': True,
            'users': users
        })

    except Exception as e:
        print(f"Error fetching available users: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@api_bp.route('/projects/<project_id>/members', methods=['POST'])
def api_add_project_member(project_id):
    """API endpoint to add a user to a project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'success': False, 'message': 'User ID is required'}), 400

    user_id = data['user_id']
    role = data.get('role')

    connection = get_db_connection('users_db')
    cursor = None

    try:
        cursor = connection.cursor()

        # Check if the project exists
        cursor.execute("SELECT COUNT(*) as count FROM projects WHERE id = UUID_TO_BIN(%s)", (project_id,))
        result = cursor.fetchone()
        if not result or result[0] == 0:
            return jsonify({'success': False, 'message': 'Project not found'}), 404

        # Check if the user exists
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE id = UUID_TO_BIN(%s)", (user_id,))
        result = cursor.fetchone()
        if not result or result[0] == 0:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Check if the user is already a member of the project
        cursor.execute(
            "SELECT COUNT(*) as count FROM project_users WHERE project_id = UUID_TO_BIN(%s) AND user_id = UUID_TO_BIN(%s)",
            (project_id, user_id)
        )
        result = cursor.fetchone()
        if result and result[0] > 0:
            return jsonify({'success': False, 'message': 'User is already a member of this project'}), 400

        # Add the user to the project
        cursor.execute(
            "INSERT INTO project_users (project_id, user_id) VALUES (UUID_TO_BIN(%s), UUID_TO_BIN(%s))",
            (project_id, user_id)
        )

        # Update user role if provided
        if role:
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = UUID_TO_BIN(%s)",
                (role, user_id)
            )

        connection.commit()

        return jsonify({'success': True, 'message': 'User added to project successfully'})

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error adding user to project: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@api_bp.route('/projects/<project_id>/members/<user_id>', methods=['DELETE'])
def api_remove_project_member(project_id, user_id):
    """API endpoint to remove a user from a project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    connection = get_db_connection('users_db')
    cursor = None

    try:
        cursor = connection.cursor()

        # Check if the user is a member of the project
        cursor.execute(
            "SELECT COUNT(*) as count FROM project_users WHERE project_id = UUID_TO_BIN(%s) AND user_id = UUID_TO_BIN(%s)",
            (project_id, user_id)
        )
        result = cursor.fetchone()
        if not result or result[0] == 0:
            return jsonify({'success': False, 'message': 'User is not a member of this project'}), 404

        # Remove the user from the project
        cursor.execute(
            "DELETE FROM project_users WHERE project_id = UUID_TO_BIN(%s) AND user_id = UUID_TO_BIN(%s)",
            (project_id, user_id)
        )
        connection.commit()

        return jsonify({'success': True, 'message': 'User removed from project successfully'})

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error removing user from project: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()