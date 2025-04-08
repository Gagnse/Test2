import uuid


def get_all_room_data(connection):
    """Create a dictionary from all rooms data, grouped by fonctional_unit and sector"""
    cursor = connection.cursor(dictionary=True)

    # Get all rooms
    cursor.execute("SELECT id, name, sector, functional_unit FROM rooms")
    rooms = cursor.fetchall()

    #print(f"Nombre de salles récupérées : {len(rooms)}")
    if not rooms:
        return {}

    # tables to include in the dictionary
    table_names = [
        "interior_fenestration", "exterior_fenestration", "doors",
        "built_in_furniture", "accessories", "plumbings",
        "fire_protection", "lighting", "electrical_outlets",
        "communication_security", "medical_equipment", "functionality",
        "arch_requirements", "struct_requirements", "risk_elements",
        "ventilation_cvac", "electricity"
    ]

    room_data = {}

    for room in rooms:
        room_id_bytes = room["id"]
        if not room_id_bytes:
            continue  # Skip if no id
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
