import uuid


def get_all_room_data(connection):
    """Construit un dictionnaire des données de toutes les salles, regroupées par unité fonctionnelle et secteur."""
    cursor = connection.cursor(dictionary=True)

    # 1️⃣ Récupérer toutes les salles
    cursor.execute("SELECT id, name, sector, functional_unit FROM rooms")
    rooms = cursor.fetchall()

    print(f"📦 Nombre de salles récupérées : {len(rooms)}")
    if not rooms:
        return {}

    # 2️⃣ Définir les tables à inclure
    table_names = [
        "interior_fenestration", "exterior_fenestration", "doors",
        "built_in_fournitures", "accessories", "plumbings",
        "fire_protection", "lighting", "electrical_outlets",
        "communication_security", "medical_equipment", "functionality",
        "arch_requirements", "struct_requirements", "risk_elements",
        "ventilation_cvac", "electricity"
    ]

    room_data = {}

    for room in rooms:
        room_id_bytes = room["id"]
        if not room_id_bytes:
            continue  # Skip si pas d'ID
        room_id = str(uuid.UUID(bytes=room_id_bytes))
        room_name = room.get("name", "Salle sans nom")
        sector = str(room.get("sector", "Secteur inconnu"))
        unit = str(room.get("functional_unit", "Unité inconnue"))

        if unit not in room_data:
            room_data[unit] = {}
        if sector not in room_data[unit]:
            room_data[unit][sector] = []

        room_entry = {
            "id": room_id,
            "name": room_name,
            "tables": {}
        }

        for table in table_names:
            try:
                query = f"SELECT * FROM {table} WHERE room_id = %s"
                cursor.execute(query, (room_id_bytes,))
                rows = cursor.fetchall()
                room_entry["tables"][table] = rows or []
            except Exception as e:
                print(f"⚠️ Erreur récupération {table} pour salle {room_id}: {e}")
                room_entry["tables"][table] = []

        room_data[unit][sector].append(room_entry)

    cursor.close()
    return room_data
