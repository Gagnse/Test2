from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file

from server.services.auth import AuthService
from server.utils.toast_helper import redirect_with_toast, set_toast
from server.database.models import Project, Organizations
from server.database.db_config import get_db_connection, database_exists
from server.services.get_room_data import get_all_room_data
import uuid
from server.services.pdf_generator import generate_pdf
from io import BytesIO

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
            'status': project.status or 'active',
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
        project_type = request.form.get('type', 'Divers')
        status = request.form.get('status', 'Actif')

        # Get the user's organization ID
        organization_id = User.get_user_org_id(user_id)

        print(f"Debug: Data received for project creation: {request.form}")

        # Sanitize project number for database name
        sanitized_number = ''.join(c for c in project_number if c.isalnum() or c in '-_')

        # Create new project with organization
        project = Project(
            project_number=sanitized_number,
            name=name,
            description=description,
            status=status,
            type=project_type,
            organization_id=organization_id
        )

        # Save the project and add the current user to it
        if project.save():
            project.add_user(user_id)

            # Get the database name for the toast message
            db_name = f"SPACELOGIC_{sanitized_number.replace('-', '_')}"

            set_toast(f'Projet créé avec succès! Base de données: {db_name}', 'success')
            return redirect(url_for('workspace.projects'))
        else:
            set_toast('Erreur lors de la création du projet.', 'error')


@workspace_bp.route('/organisations')
def organisations():
    """Organizations page for current user"""
    user_id = AuthService.get_current_user_id()
    print(f"Current user ID: {user_id}")

    # Get the first organization for this user
    # Since a user belongs to only one organization according to schema
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
        current_user = User.find_by_id(user_id)
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
            # Default role is Membre
            role_name = 'Membre'

            # First check if the user is the super admin
            if member.id == org.super_admin_id:
                role_name = 'Administrateur'
                print(f"User {member.id} is super admin, setting role to Administrateur")
            else:
                # Get roles from regular role assignments
                roles = org.get_user_roles(member.id)
                if roles:
                    role_name = roles[0]['name']
                    print(f"Using assigned role {role_name} for user {member.id}")
                # Fallback to the role stored in the user table if available
                elif hasattr(member, 'role') and member.role:
                    role_name = member.role
                    print(f"Using role from user table: {role_name} for user {member.id}")

            members_list.append({
                'id': member.id,
                'last_name': member.last_name,
                'first_name': member.first_name,
                'email': member.email,
                'created_at': member.created_at,
                'is_active': member.is_active,
                'role': role_name,
                'department': member.department,
                'location': member.location
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
            'status': proj.status or 'active',
            'type': proj.type or 'Divers'
        })

    # Get roles for this organization
    roles_list = org.get_roles()
    print(f"Retrieved {len(roles_list)} roles")

    # Create the organization data structure
    organisation = {
        'id': org.id,
        'name': org.name,
        'created_at': org.created_at,
        'super_admin_id': org.super_admin_id,
        'members': members_list,
        'projects': project_list,
        'roles': roles_list,
    }

    return render_template('workspace/organisations.html', organisation=organisation)


@workspace_bp.route('/organisations/<org_id>')
def organisation_detail(org_id):
    """Organization detail page"""
    # Get the organization details using the Organization model
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

#route pour afficher les données du projet
@workspace_bp.route('/projects/<project_id>')
def project_detail(project_id):

    # 1️⃣ Se connecter à `users_db`
    connection = get_db_connection('users_db')
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT project_number, name, description, start_date, end_date, status, type 
        FROM projects 
        WHERE id = UUID_TO_BIN(%s);
    """, (project_id,))
    project = cursor.fetchone()

    cursor.close()
    connection.close()

    # Vérifier si le projet existe
    if not project:
        return "Erreur : Projet introuvable", 404

    project_number = project['project_number']
    project_name = project['name']

    # Créer le nom de la bd
    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    # Créer un dictionnaire complet avec toutes les informations du projet
    project_details = {
        'id': project_id,
        'name': project_name,
        'project_number': project_number,
        'description': project.get('description', 'Détails du projet'),
        'start_date': project.get('start_date'),
        'end_date': project.get('end_date'),
        'status': project.get('status', 'Actif'),
        'type': project.get('type', 'Non défini')
    }

    print(f"✅ Projet trouvé : {project_name} → Connexion à {project_db_name}")

    # Vérifier si la base existe avant de se connecter
    if not database_exists(project_db_name):
        return f"Erreur : La base de données {project_db_name} n'existe pas", 404

    # Connexion à la base spécifique au projet
    connection = get_db_connection(project_db_name)
    if not connection:
        return f"Erreur : Impossible de se connecter à {project_db_name}", 500

    cursor = connection.cursor(dictionary=True)

    # Récupération des données des différentes tables
    project_data = {}
    tables = [
        "interior_fenestration", "exterior_fenestration", "doors",
        "built_in_fournitures", "accessories", "plumbings",
        "fire_protection", "lighting", "electrical_outlets",
        "communication_security", "medical_equipment",
        "functionality", "arch_requirements", "struct_requirements",
        "risk_elements", "ventilation_cvac", "electricity"
    ]

    for table in tables:
        try:
            primary_key = f"{table}_id"

            cursor.execute(f"""
                SELECT {table}.*, {table}.{primary_key}, rooms.id AS room_id, rooms.name AS room_name 
                FROM {table} 
                LEFT JOIN rooms ON {table}.room_id = rooms.id;
            """)

            rows = cursor.fetchall() or []

            # Convertir l'ID binaire en UUID
            for row in rows:
                if primary_key in row and isinstance(row[primary_key], bytes):
                    row[primary_key] = str(uuid.UUID(bytes=row[primary_key]))  # Convertir en UUID string
                if "room_id" in row and isinstance(row["room_id"], bytes):
                    row["room_id"] = str(uuid.UUID(bytes=row["room_id"]))  # Convertir en UUID string

            project_data[table] = rows
            print(f"🔹 {table}: {len(rows)} lignes")

        except Exception as err:
            print(f"⚠️ Erreur récupération {table} : {err}")
            project_data[table] = []  # Assure une liste vide en cas d'erreur

    # Récupérer les salles groupées par unité fonctionnelle et secteur
    cursor.execute("""
        SELECT id, name, sector, functional_unit 
        FROM rooms
        ORDER BY functional_unit, sector, name;
    """)
    rooms = cursor.fetchall()

    if not rooms:
        print("⚠️ Aucune salle récupérée depuis la base de données !")

    # Menu de gauche : Organisation des données sous forme d'arborescence {Unité fonctionnelle -> Secteur -> Salles}
    room_hierarchy = {}
    for room in rooms:
        room_id = str(uuid.UUID(bytes=room['id']))  # Convertir en UUID string
        room_name = room['name']
        sector = room['sector']
        functional_unit = room['functional_unit']

        if functional_unit not in room_hierarchy:
            room_hierarchy[functional_unit] = {}

        if sector not in room_hierarchy[functional_unit]:
            room_hierarchy[functional_unit][sector] = []

        room_hierarchy[functional_unit][sector].append({'id': room_id, 'name': room_name})

    # Trier unités fonctionnelles du plus petit au plus grand
    room_hierarchy = {k: room_hierarchy[k] for k in
                      sorted(room_hierarchy.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))}

    print(f"📂 Hiérarchie des salles triée : {room_hierarchy}")

    cursor.close()
    connection.close()

    # Définir les colonnes à afficher pour chaque catégorie
    columns_to_display = {
        "interior_fenestration": ["interior_fenestration_category", "interior_fenestration_number",
                                  "interior_fenestration_name", "interior_fenestration_quantity"],
        "exterior_fenestration": ["exterior_fenestration_category", "exterior_fenestration_number",
                                  "exterior_fenestration_name", "exterior_fenestration_quantity"],
        "doors": ["doors_category", "doors_number", "doors_name", "doors_quantity"],
        "built_in_fournitures": ["built_in_fournitures_category", "built_in_fournitures_number",
                                 "built_in_fournitures_name", "built_in_fournitures_quantity"],
        "accessories": ["accessories_category", "accessories_number", "accessories_name", "accessories_quantity"],
        "plumbings": ["plumbings_category", "plumbings_number", "plumbings_name", "plumbings_quantity"],
        "fire_protection": ["fire_protection_category", "fire_protection_number", "fire_protection_name",
                            "fire_protection_quantity"],
        "lighting": ["lighting_category", "lighting_number", "lighting_name", "lighting_quantity"],
        "electrical_outlets": ["electrical_outlets_category", "electrical_outlets_number", "electrical_outlets_name",
                               "electrical_outlets_quantity"],
        "communication_security": ["communication_security_category", "communication_security_number",
                                   "communication_security_name", "communication_security_quantity"],
        "medical_equipment": ["medical_equipment_category", "medical_equipment_number", "medical_equipment_name",
                              "medical_equipment_quantity"],
        "functionality": ["functionality_occupants_number", "functionality_schedule", "functionality_access",
                          "functionality_description"],
        "arch_requirements": ["arch_requirements_critic_length", "arch_requirements_critic_width",
                              "arch_requirements_critic_height"],
        "struct_requirements": ["struct_requirements_floor_overload_required",
                                "struct_requirements_vibrations_sensitivity"],
        "risk_elements": ["risk_elements_general", "risk_elements_gas", "risk_elements_liquids"],
        "ventilation_cvac": ["ventilation_care_area_type", "ventilation_specific_exhaust"],
        "electricity": ["electricity_lighting_type", "electricity_lighting_level"]
    }

    print(f"📊 Données envoyées à `project_detail.html` : {list(project_data.keys())}")

    selected_room_id = request.args.get('room_id', None)
    selected_room_name = None

    # Filtrer les données pour les onglets spéciaux
    filtered_functionality = []
    if selected_room_id:
        filtered_functionality = [f for f in project_data.get("functionality", []) if
                                  f.get("room_id") == selected_room_id]

        # Trouver le nom de la salle
        for f in project_data.get("functionality", []):
            if f.get("room_id") == selected_room_id:
                selected_room_name = f.get("room_name")
                break

    # Convertir les sets en listes pour JSON
    def convert_sets_to_lists(data):
        if isinstance(data, dict):
            return {k: convert_sets_to_lists(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_sets_to_lists(v) for v in data]
        elif isinstance(data, set):
            return list(data)  # Convertir les sets en liste
        return data

    # Appliquer la conversion
    project_data = convert_sets_to_lists(project_data)

    return render_template("workspace/project_detail.html",
                           project=project_details,  # Utiliser les détails complets du projet
                           project_data=project_data,
                           filtered_functionality=filtered_functionality,
                           columns_to_display=columns_to_display,
                           room_hierarchy=room_hierarchy,
                           selected_room_id=selected_room_id,
                           selected_room_name=selected_room_name,
                           )

#route pour ajouter un tuple dans les onglets normaux
@workspace_bp.route('/projects/<project_id>/add_item', methods=['POST'])
def add_item(project_id):
    project_db_name = f"SPACELOGIC_{project_id.replace('-', '')}"

    # Vérifier si la bd projet existe
    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    # On récupère les données envoyées en JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400
    category = data.get("category")
    new_data = data.get("new_data")
    room_id = data.get("room_id")

    if not category or not new_data or not room_id:
        return jsonify({"Success": False, "message": "Données invalides"}), 400
    new_data["room_id"] = uuid.UUID(room_id).bytes

    # Connexion à la base de données
    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    # Générer UUID pour id du nouveau tuple
    new_id = uuid.uuid4().bytes

    # Requête SQL
    columns = ["{}_id".format(category)] + list(new_data.keys())
    values = [new_id] + list(new_data.values())

    placeholders = ", ".join(["%s"] * len(values))
    columns = ", ".join(columns)

    query = f"INSERT INTO {category} ({columns}) VALUES ({placeholders})"

    try:
        cursor.execute(query, values)
        connection.commit()
        return jsonify({"success": True, "message": "Élément ajouté avec succès", "id": str(uuid.UUID(bytes=new_id))})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#route pour supprimer un tuple dans les onglets normaux
@workspace_bp.route('/projects/<project_id>/delete_item', methods=['POST'])
def delete_item(project_id):
    project_db_name = f"SPACELOGIC_{project_id.replace('-', '')}"
    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    item_id = data.get("id")
    category = data.get("category")

    if not item_id or not category:
        return jsonify({"success": False, "message": "Paramètres manquants"}), 400

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        # Supprimer dans la bonne table
        query = f"DELETE FROM {category} WHERE {category}_id = UNHEX(REPLACE(%s, '-', ''))"
        cursor.execute(query, (item_id,))
        connection.commit()
        return jsonify({"success": True, "message": "Élément supprimé avec succès"})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur lors de la suppression : {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#route pour modifier un tuple dans les onglets normaux
@workspace_bp.route('/projects/<project_id>/edit_item', methods=['POST'])
def edit_item(project_id):
    """Modification d'un élément spécifique"""

    # Create database name using UUID without hyphens
    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    # Get current user ID for tracking changes
    user_id = AuthService.get_current_user_id()

    # 🔄 Traiter les données reçues
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    item_id = data.get("id")
    category = data.get("category")
    updated_data = data.get("updatedData")

    if not item_id or not category or not updated_data:
        return jsonify({"success": False, "message": "Données incomplètes"}), 400

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = None

    try:
        # Set current user for tracking changes
        set_current_user(connection, user_id)

        cursor = connection.cursor()

        # 🔍 Vérifier et corriger l'ID
        try:
            if isinstance(item_id, str):
                item_id = item_id.strip()

                if item_id.startswith("b'") and item_id.endswith("'"):
                    item_id = item_id[2:-1]
                    hex_str = item_id.replace("\\x", "")
                    item_id = bytes.fromhex(hex_str)
                else:
                    item_id = uuid.UUID(item_id).bytes

            elif isinstance(item_id, bytes) and len(item_id) == 16:
                pass
            else:
                raise ValueError("Format ID invalide")

        except ValueError as e:
            return jsonify({"success": False, "message": f"ID invalide : {e}"}), 400

        # Vérifier que l'ID existe dans la base
        check_query = f"SELECT COUNT(*) FROM {category} WHERE {category}_id = %s"
        cursor.execute(check_query, (item_id,))
        result = cursor.fetchone()

        if result[0] == 0:
            return jsonify({"success": False, "message": "ID introuvable en base de données"}), 404

        # Construire la requête UPDATE
        set_clause = ", ".join(f"{key} = %s" for key in updated_data.keys())
        values = list(updated_data.values()) + [item_id]

        query = f"UPDATE {category} SET {set_clause} WHERE {category}_id = %s"

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Aucune modification effectuée"}), 404
        return jsonify({"success": True, "message": "Modification enregistrée"})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500

    finally:
        cursor.close()
        connection.close()

#route pour modifier l'onglet fonctionalité
@workspace_bp.route('/projects/<project_id>/edit_functionality', methods=['POST'])
def edit_functionality(project_id):
    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    room_id = data.get("room_id")
    try:
        room_id = uuid.UUID(room_id).bytes
    except Exception:
        return jsonify({"success": False, "message": "ID de salle invalide"}), 400

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        query = """
            UPDATE functionality
            SET functionality_occupants_number = %s,
                functionality_desk_number = %s,
                functionality_lab_number = %s,
                functionality_schedule = %s,
                functionality_access = %s,
                functionality_description = %s,
                functionality_proximity = %s,
                functionality_commentary = %s,
                functionality_consideration = %s
            WHERE room_id = %s
        """
        values = (
            data.get("functionality_occupants_number"),
            data.get("functionality_desk_number"),
            data.get("functionality_lab_number"),
            data.get("functionality_schedule"),
            ",".join(data.get("functionality_access", [])),
            data.get("functionality_description"),
            data.get("functionality_proximity"),
            data.get("functionality_commentary"),
            ",".join(data.get("functionality_consideration", [])),
            room_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Aucune ligne modifiée"}), 404

        return jsonify({"success": True, "message": "Modification enregistrée"})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500

    finally:
        cursor.close()
        connection.close()

#route pour modifier l'onglet exigences architecturales
@workspace_bp.route('/projects/<project_id>/edit_arch_requirements', methods=['POST'])
def edit_arch_requirements(project_id):
    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    data = request.get_json(silent=True)
    print("📥 Données reçues :", json.dumps(data, indent=2))

    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    try:
        room_id = uuid.UUID(data.get("room_id")).bytes
    except Exception:
        return jsonify({"success": False, "message": "ID de salle invalide"}), 400

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        query = """
            UPDATE arch_requirements
            SET
                arch_requirements_critic_length = %s,
                arch_requirements_critic_width = %s,
                arch_requirements_critic_height = %s,
                arch_requirements_validation_req = %s,
                arch_requirements_acoustic = %s,
                arch_requirements_int_fenestration = %s,
                arch_requirements_int_fen_adj_room = %s,
                arch_requirements_int_fen_other = %s,
                arch_requirements_ext_fenestration = %s,
                arch_requirements_ext_fen_solar_blind = %s,
                arch_requirements_ext_fen_opaque_blind = %s,
                arch_requirements_commentary = %s
            WHERE room_id = %s
        """
        values = (
            data.get("arch_requirements_critic_length"),
            data.get("arch_requirements_critic_width"),
            data.get("arch_requirements_critic_height"),
            data.get("arch_requirements_validation_req"),
            data.get("arch_requirements_acoustic"),
            ",".join(data.get("arch_requirements_int_fenestration", [])),
            data.get("arch_requirements_int_fen_adj_room"),
            data.get("arch_requirements_int_fen_other"),
            ",".join(data.get("arch_requirements_ext_fenestration", [])),
            data.get("arch_requirements_ext_fen_solar_blind"),
            data.get("arch_requirements_ext_fen_opaque_blind"),
            data.get("arch_requirements_commentary"),
            room_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Aucune ligne modifiée"}), 404

        return jsonify({"success": True, "message": "Modifications enregistrées"})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#route pour modifier l'onglet exigences structurales
@workspace_bp.route('/projects/<project_id>/edit_struct_requirements', methods=['POST'])
def edit_struct_requirements(project_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    room_id = data.get("room_id")
    try:
        room_id = uuid.UUID(room_id).bytes
    except Exception:
        return jsonify({"success": False, "message": "ID de salle invalide"}), 400

    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        query = """
            UPDATE struct_requirements
            SET struct_requirements_floor_overload_required = %s,
                struct_requirements_overload = %s,
                struct_requirements_equipment_weight = %s,
                struct_requirements_floor_flatness = %s,
                struct_requirements_ditch_gutter = %s,
                struct_requirements_steel_sensitivity = %s,
                struct_requirements_equipment_other = %s,
                struct_requirements_vibrations_sensitivity = %s,
                struct_requirements_max_vibrations = %s,
                struct_requirements_commentary = %s
            WHERE room_id = %s
        """
        values = (
            data.get("struct_requirements_floor_overload_required"),
            data.get("struct_requirements_overload"),
            data.get("struct_requirements_equipment_weight"),
            data.get("struct_requirements_floor_flatness"),
            data.get("struct_requirements_ditch_gutter"),
            data.get("struct_requirements_steel_sensitivity"),
            data.get("struct_requirements_equipment_other"),
            data.get("struct_requirements_vibrations_sensitivity"),
            data.get("struct_requirements_max_vibrations"),
            data.get("struct_requirements_commentary"),
            room_id
        )
        cursor.execute(query, values)
        connection.commit()
        return jsonify({"success": True})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#route pour modifier l'onglet éléments à risque
@workspace_bp.route('/projects/<project_id>/edit_risk_elements', methods=['POST'])
def edit_risk_elements(project_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    room_id = data.get("room_id")
    
    try:
        room_id = uuid.UUID(room_id).bytes
    except Exception:
        return jsonify({"success": False, "message": "ID de salle invalide"}), 400

    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        query = """
            UPDATE risk_elements
            SET risk_elements_general = %s,
                risk_elements_general_radioactive = %s,
                risk_elements_biological = %s,
                risk_elements_gas = %s,
                risk_elements_gas_qty = %s,
                risk_elements_gas_toxic_gas = %s,
                risk_elements_liquids = %s,
                risk_elements_liquids_qty = %s,
                risk_elements_liquids_cryogenic = %s,
                risk_elements_other = %s,
                risk_elements_chemical_products = %s,
                risk_elements_commentary = %s
            WHERE room_id = %s
        """

        values = (
            ",".join(data.get("risk_elements_general", [])),
            data.get("risk_elements_general_radioactive"),
            ",".join(data.get("risk_elements_biological", [])),
            ",".join(data.get("risk_elements_gas", [])),
            data.get("risk_elements_gas_qty"),
            data.get("risk_elements_gas_toxic_gas"),
            ",".join(data.get("risk_elements_liquids", [])),
            data.get("risk_elements_liquids_qty"),
            data.get("risk_elements_liquids_cryogenic"),
            ",".join(data.get("risk_elements_other", [])),
            data.get("risk_elements_chemical_products"),
            data.get("risk_elements_commentary"),
            room_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Aucune ligne modifiée"}), 404

        return jsonify({"success": True, "message": "Modifications enregistrées"})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#route pour modifier l'onglet ventilation CVAC
@workspace_bp.route('/projects/<project_id>/edit_ventilation_cvac', methods=['POST'])
def edit_ventilation_cvac(project_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    room_id = data.get("room_id")
    try:
        room_id = uuid.UUID(room_id).bytes
    except Exception:
        return jsonify({"success": False, "message": "ID de salle invalide"}), 400

    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        query = """
            UPDATE ventilation_cvac
            SET ventilation_care_area_type = %s,
                ventilation = %s,
                ventilation_special_mechanics = %s,
                ventilation_specific_exhaust = %s,
                ventilation_commentary = %s,
                ventilation_relative_room_pressure = %s,
                ventilation_pressurization = %s,
                ventilation_environmental_parameters = %s
            WHERE room_id = %s
        """
        values = (
            data.get("ventilation_care_area_type"),
            data.get("ventilation"),
            data.get("ventilation_special_mechanics"),
            data.get("ventilation_specific_exhaust"),
            data.get("ventilation_commentary"),
            data.get("ventilation_relative_room_pressure"),
            data.get("ventilation_pressurization"),
            data.get("ventilation_environmental_parameters"),
            room_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Aucune ligne modifiée"}), 404

        return jsonify({"success": True, "message": "Modification enregistrée"})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#modifier onglet électricitié
@workspace_bp.route('/projects/<project_id>/edit_electricity', methods=['POST'])
def edit_electricity(project_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Aucune donnée reçue"}), 400

    room_id = data.get("room_id")
    try:
        room_id = uuid.UUID(room_id).bytes
    except Exception:
        return jsonify({"success": False, "message": "ID de salle invalide"}), 400

    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    if not database_exists(project_db_name):
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor()

    try:
        query = """
            UPDATE electricity
            SET electricity_care_area_type = %s,
                electricity_smoke_fire_detection = %s,
                electricity_special_equipment = %s,
                electricity_lighting_type = %s,
                electricity_lighting_level = %s,
                electricity_lighting_control = %s,
                color_temperature = %s,
                electricity_lighting = %s,
                electricity_commentary = %s
            WHERE room_id = %s
        """
        values = (
            data.get("electricity_care_area_type"),
            data.get("electricity_smoke_fire_detection"),
            data.get("electricity_special_equipment"),
            data.get("electricity_lighting_type"),
            data.get("electricity_lighting_level"),
            data.get("electricity_lighting_control"),
            data.get("color_temperature"),
            data.get("electricity_lighting"),
            data.get("electricity_commentary"),
            room_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Aucune ligne modifiée"}), 404

        return jsonify({"success": True, "message": "Modification enregistrée"})

    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": f"Erreur SQL : {e}"}), 500
    finally:
        cursor.close()
        connection.close()

#route pour ajouter une pièce
@workspace_bp.route('/projects/<project_id>/add_room', methods=['POST'])
def add_room(project_id):
    """API endpoint to add a new room to a project"""
    if not AuthService.is_authenticated():
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    # Get the data from the request
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400

    # Validate required fields
    required_fields = ['program_number', 'name', 'planned_area']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'Le champ {field} est requis'}), 400

    # Create clean UUID for database name
    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"

    # Check if database exists
    if not database_exists(project_db_name):
        return jsonify({'success': False, 'message': f'Base de données {project_db_name} introuvable'}), 404

    # Connect to the project database
    connection = get_db_connection(project_db_name)
    if not connection:
        return jsonify({'success': False, 'message': f'Impossible de se connecter à {project_db_name}'}), 500

    cursor = connection.cursor()

    try:
        # Check if program_number already exists
        cursor.execute("SELECT COUNT(*) FROM rooms WHERE program_number = %s", (data['program_number'],))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({
                'success': False,
                'message': 'Une salle avec ce numéro de programme existe déjà. Veuillez utiliser un numéro unique.'
            }), 400

        # Insert the new room
        query = """
            INSERT INTO rooms (
                program_number, name, description, sector, 
                functional_unit, level, planned_area
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['program_number'],
            data['name'],
            data.get('description', ''),
            data.get('sector', ''),
            data.get('functional_unit', ''),
            data.get('level', ''),
            data['planned_area']
        )

        cursor.execute(query, values)

        # Get the new room ID
        cursor.execute("SELECT BIN_TO_UUID(id) FROM rooms WHERE program_number = %s", (data['program_number'],))
        room_id = cursor.fetchone()[0]

        # Initialize additional tables with default values
        # This will ensure all tabs display something for this room

        # Insert default functionality record
        cursor.execute("""
            INSERT INTO functionality (room_id, functionality_occupants_number) 
            VALUES (UUID_TO_BIN(%s), 1)
        """, (room_id,))

        # Insert default arch_requirements record
        cursor.execute("""
            INSERT INTO arch_requirements (room_id, arch_requirements_critic_length, 
                       arch_requirements_critic_width, arch_requirements_critic_height) 
            VALUES (UUID_TO_BIN(%s), 3, 3, 2)
        """, (room_id,))

        # Insert default risk_elements record
        cursor.execute("""
            INSERT INTO risk_elements (room_id, risk_elements_general) 
            VALUES (UUID_TO_BIN(%s), 'NA')
        """, (room_id,))

        # Insert default ventilation_cvac record
        cursor.execute("""
            INSERT INTO ventilation_cvac (room_id, ventilation_care_area_type) 
            VALUES (UUID_TO_BIN(%s), 'Standard')
        """, (room_id,))

        # Insert default electricity record
        cursor.execute("""
            INSERT INTO electricity (room_id, electricity_care_area_type) 
            VALUES (UUID_TO_BIN(%s), 'Standard')
        """, (room_id,))

        connection.commit()

        return jsonify({
            'success': True,
            'message': 'Salle créée avec succès',
            'room': {
                'id': room_id,
                'program_number': data['program_number'],
                'name': data['name']
            }
        })

    except Exception as e:
        connection.rollback()
        print(f"Error creating room: {e}")
        return jsonify({'success': False, 'message': f'Erreur lors de la création de la salle: {str(e)}'}), 500

    finally:
        cursor.close()
        connection.close()

#génération du rapport en pdf
@workspace_bp.route('/projects/<project_id>/generate_pdf', methods=['GET'])
def generate_pdf(project_id):

    clean_uuid = project_id.replace('-', '')
    project_db_name = f"SPACELOGIC_{clean_uuid}"
    print(f"🔍 Vérification de l'existence de la base : {project_db_name}")

    if not database_exists(project_db_name):
        print(f"❌ La base {project_db_name} n'existe pas")
        return jsonify({"success": False, "message": "Base de données introuvable"}), 404
    print(f"✅ La base {project_db_name} existe : True")

    connection = get_db_connection(project_db_name)
    cursor = connection.cursor(dictionary=True)
    print(f"🔄 Tentative de connexion à MySQL: {project_db_name} sur localhost:3306")

    try:
        # Connexion à la base users_db pour récupérer le nom du projet
        users_connection = get_db_connection("users_db")
        users_cursor = users_connection.cursor(dictionary=True)

        users_cursor.execute("""
            SELECT 
                project_number,
                name,
                description,
                start_date,
                end_date,
                status,
                type
            FROM projects 
            WHERE id = UUID_TO_BIN(%s)
        """, (project_id,))
        project_info = users_cursor.fetchone()

        if not project_info:
            print("❌ Projet introuvable dans users_db")
            return jsonify({"success": False, "message": "Projet introuvable"}), 404

        users_cursor.close()
        users_connection.close()

        # Charger toutes les données de salle, triées
        room_data_dict = get_all_room_data(connection)

        if not room_data_dict:
            print("❌ Aucune salle trouvée pour générer le PDF.")
            return jsonify({"success": False, "message": "Aucune salle trouvée"}), 400

        print("🗂️ Unités fonctionnelles trouvées :", list(room_data_dict.keys()))

        # Générer le PDF
        from server.services.pdf_generator import generate_pdf
        pdf_path = generate_pdf(project_info, room_data_dict)
        print(f"📄 Rapport PDF généré : {pdf_path}")

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        print(f"❌ Erreur PDF : {e}")
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

#route pour afficher les données du projet dans parameters
@workspace_bp.route('/projects/<project_id>/project_parameters', methods=['GET', 'POST'])
def project_parameters(project_id):
    users_connection = get_db_connection("users_db")
    users_cursor = users_connection.cursor(dictionary=True)

    # 📥 Charger les données existantes AVANT le POST
    select_query = """
        SELECT project_number, name, description,
               DATE(start_date) AS start_date,
               DATE(end_date) AS end_date,
               status, type
        FROM projects
        WHERE id = UUID_TO_BIN(%s)
    """
    users_cursor.execute(select_query, (project_id,))
    project = users_cursor.fetchone()

    if request.method == 'POST':
        data = request.form

        update_query = """
            UPDATE projects SET
                project_number = %s,
                name = %s,
                description = %s,
                start_date = %s,
                end_date = %s,
                status = %s,
                type = %s
            WHERE id = UUID_TO_BIN(%s)
        """
        users_cursor.execute(update_query, (
            data['project_number'],
            data['name'],
            data['description'],
            project['start_date'],  # 👈 Tu peux maintenant l'utiliser
            data['end_date'] or None,
            data['status'],
            data['type'],
            project_id
        ))
        users_connection.commit()
        users_cursor.close()
        users_connection.close()

        return redirect(url_for('workspace.project_detail', project_id=project_id))

    users_cursor.close()
    users_connection.close()

    return render_template('workspace/project_parameters.html', project=project, project_id=project_id)







