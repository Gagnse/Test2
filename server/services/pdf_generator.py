from fpdf import FPDF
import tempfile
import unicodedata
from datetime import datetime

mois_fr = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril",
    5: "mai", 6: "juin", 7: "juillet", 8: "août",
    9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}

def format_date_fr(date_value):
    """format the date to show as requested (jour mois année)"""
    try:
        if not date_value:
            return "Aucun"
        if isinstance(date_value, str):
            date_value = datetime.fromisoformat(date_value)
        return f"{date_value.day} {mois_fr[date_value.month]} {date_value.year}"
    except Exception:
        return "Aucun"

def clean_text(text):
    """clean text to generate PDF"""
    return str(text) if text is not None else ""

def auto_font_size(pdf, text, max_width, base_size=10, min_size=6):
    """auto font size"""
    font_size = base_size
    while font_size >= min_size:
        pdf.set_font("DejaVu", size=font_size)
        if pdf.get_string_width(text) <= max_width:
            return font_size
        font_size -= 0.5
    return min_size

def draw_checkbox_row(pdf, label_list, checked_values, col_count=2, label_width=70):
    """draw checkbox row"""
    pdf.set_font("DejaVu", size=10)
    items = list(label_list)
    mid = (len(items) + 1) // col_count

    for i in range(mid):
        for j in range(col_count):
            idx = i + j * mid
            if idx < len(items):
                label = items[idx]
                checkbox = "☑" if label in checked_values else "☐"
                pdf.cell(label_width, 8, f"{checkbox} {label}", ln=0)
        pdf.ln()

def generate_pdf(project_info, room_data_dict):
    """generate PDF report"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Charge DejaVu font
    font_path = "fonts/DejaVuSans.ttf"
    font_bold_path = "fonts/DejaVuSans-Bold.ttf"
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_font("DejaVu", "B", font_bold_path, uni=True)
    pdf.set_font("DejaVu", size=10)

    # project header
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, f"{project_info['name']} (#{project_info['project_number']})", ln=True)

    pdf.set_font("DejaVu", size=10)

    status = project_info.get("status") or "Aucun"
    type_ = project_info.get("type") or "Aucun"
    start = format_date_fr(project_info.get("start_date")) or "Aucun"
    end = format_date_fr(project_info.get("end_date")) or "Aucun"

    pdf.cell(0, 8, f"Statut : {status}", ln=True)
    pdf.cell(0, 8, f"Type : {type_}", ln=True)
    pdf.cell(0, 8, f"Début du projet : {start}", ln=True)
    pdf.cell(0, 8, f"Fin du projet : {end}", ln=True)

    pdf.ln(3)
    pdf.set_font("DejaVu", style="B", size=10)
    pdf.cell(0, 8, "Description :", ln=True)

    pdf.set_font("DejaVu", size=10)
    description = project_info.get("description", "")
    pdf.multi_cell(0, 8, description)
    pdf.ln(5)

    tab_titles = {
        "exterior_fenestration": "Fenestration Extérieure",
        "interior_fenestration": "Fenestration Intérieure",
        "doors": "Portes",
        "built_in_furniture": "Mobilier Intégré",
        "accessories": "Accessoires",
        "plumbings": "Plomberie",
        "fire_protection": "Protection Incendie",
        "lighting": "Éclairage",
        "electrical_outlets": "Prises Électriques",
        "communication_security": "Communication & Sécurité",
        "medical_equipment": "Équipements Médicaux",
        "functionality": "Fonctionnalité",
        "arch_requirements": "Exigences Architecturales",
        "struct_requirements": "Exigences Structurales",
        "risk_elements": "Éléments à Risque",
        "ventilation_cvac": "Ventilation CVAC",
        "electricity": "Électricité"
    }

    access_labels = {
        "client_access": "Accès clients",
        "stretcher_access": "Accès civière",
        "bed_access": "Accès lits",
        "patients_access": "Accès patients",
        "exterior_access": "Accès extérieur",
        "hallway_access": "Accès corridor",
        "adj_room_access": "Accès pièce adjacente",
        "other": "Autre"
    }

    consideration_labels = {
        "NA": "N/A",
        "anti_suicide": "Antisuicide",
        "waterproof": "Étanchéité",
        "radiation": "Radiation",
        "electromagnetic": "Électromagnétique",
        "sterile": "Milieu stérile",
        "vibrations_sensitivity": "Sensible vibrations",
        "wet_lab": "Labo humide",
        "dry_lab": "Labo sec",
        "biosecurity": "Biosécurité",
        "pet_shop": "Animalerie"
    }

    int_fenestration_labels = {
        "not_required": "Non requis",
        "with_hallway": "Avec couloir",
        "clear_glass": "Verre clair",
        "frosted_glass": "Verre givré",
        "semi_frosted_glass": "Semi-givré",
        "one_way_glass": "Sens unique",
        "integrated_blind": "Store intégré"
    }

    ext_fenestration_labels = {
        "not_required": "Non requis",
        "required": "Requis",
        "total_obscurity": "Obscurité totale",
        "frosted_glass": "Verre givré",
        "tinted_glass": "Verre teinté",
        "integrated_blind": "Store intégré"
    }

    special_tables = {
        'functionality', 'arch_requirements', 'struct_requirements',
        'risk_elements', 'ventilation_cvac', 'electricity'
    }

    for level in sorted(room_data_dict):
        for zone in sorted(room_data_dict[level]):
            for room in room_data_dict[level][zone]:
                room_name = clean_text(room['name'])

                pdf.add_page()
                pdf.set_font("DejaVu", "B", size=12)
                pdf.cell(0, 10, room_name, ln=True)
                pdf.ln(5)

                room_tables = room.get("tables", {})
                for table_name, table_data in room_tables.items():
                    if not isinstance(table_data, list) or not table_data:
                        continue

                    table_title = clean_text(tab_titles.get(table_name, table_name.replace('_', ' ').capitalize()))

                    pdf.set_fill_color(230, 240, 255)  # bleu pâle
                    pdf.set_font("DejaVu", "B", size=10)
                    pdf.cell(0, 10, table_title, ln=True, fill=True)
                    pdf.set_font("DejaVu", size=10)

                    if table_name == "functionality":
                        for entry in table_data:
                            pdf.cell(60, 8, "Nb occupants :", ln=0)
                            pdf.cell(60, 8, str(entry.get("functionality_occupants_number", "")), ln=1)

                            pdf.cell(60, 8, "Nb postes travail - Bureau :", ln=0)
                            pdf.cell(60, 8, str(entry.get("functionality_desk_number", "")), ln=1)

                            pdf.cell(60, 8, "Nb postes travail - Labo :", ln=0)
                            pdf.cell(60, 8, str(entry.get("functionality_lab_number", "")), ln=1)

                            pdf.cell(60, 8, "Horaire typique :", ln=0)
                            pdf.cell(60, 8, clean_text(entry.get("functionality_schedule", "")), ln=1)

                            pdf.cell(60, 8, "Description :", ln=0)
                            pdf.multi_cell(0, 8, clean_text(entry.get("functionality_description", "")))

                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Accès requis :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            checked_access = entry.get("functionality_access") or ""
                            checked_access = checked_access.split(',') if isinstance(checked_access, str) else list(
                                checked_access)
                            draw_checkbox_row(pdf, access_labels.values(),
                                              [access_labels[k] for k in checked_access if k in access_labels])

                            pdf.ln(3)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Considérations :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            cons_set = entry.get("functionality_consideration") or ""
                            checked_cons = cons_set.split(',') if isinstance(cons_set, str) else list(cons_set)
                            draw_checkbox_row(pdf, consideration_labels.values(),
                                              [consideration_labels[k] for k in checked_cons if
                                               k in consideration_labels])

                            pdf.ln(5)

                    elif table_name == "arch_requirements":
                        for entry in table_data:
                            def draw_field(label, key):
                                pdf.cell(60, 8, f"{label} :", ln=0)
                                pdf.cell(60, 8, str(entry.get(key, "")), ln=1)

                            draw_field("Longueur critique (mm)", "arch_requirements_critic_length")
                            draw_field("Largeur critique (mm)", "arch_requirements_critic_width")
                            draw_field("Hauteur critique (mm)", "arch_requirements_critic_height")
                            val_req = "Oui" if str(entry.get("arch_requirements_validation_req")) == "1" else "Non"
                            pdf.cell(60, 8, "Validation requise :", ln=0)
                            pdf.cell(60, 8, val_req, ln=1)

                            pdf.cell(60, 8, "Acoustique (STC) :", ln=0)
                            pdf.cell(60, 8, str(entry.get("arch_requirements_acoustic", "")), ln=1)

                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Fenestration intérieure :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            checked = entry.get("arch_requirements_int_fenestration") or ""
                            checked = checked.split(',') if isinstance(checked, str) else list(checked)
                            draw_checkbox_row(pdf, int_fenestration_labels.values(),
                                              [int_fenestration_labels[k] for k in checked if
                                               k in int_fenestration_labels])
                            pdf.cell(60, 8, "Pièce adjacente :", ln=0)
                            pdf.cell(60, 8, clean_text(entry.get("arch_requirements_int_fen_adj_room", "")), ln=1)

                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Fenestration extérieure :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            checked = entry.get("arch_requirements_ext_fenestration") or ""
                            checked = checked.split(',') if isinstance(checked, str) else list(checked)
                            draw_checkbox_row(pdf, ext_fenestration_labels.values(),
                                              [ext_fenestration_labels[k] for k in checked if
                                               k in ext_fenestration_labels])
                            pdf.cell(60, 8, "Commentaire :", ln=0)
                            pdf.multi_cell(0, 8, clean_text(entry.get("arch_requirements_commentary", "")))

                            pdf.ln(5)

                    elif table_name == "struct_requirements":
                        for entry in table_data:
                            def bool_to_oui_non(val):
                                return "Oui" if str(val) == "1" else "Non"

                            fields = [
                                ("Surcharge au sol requise",
                                 bool_to_oui_non(entry.get("struct_requirements_floor_overload_required"))),
                                ("Surcharge (kg/m²)", entry.get("struct_requirements_overload", "")),
                                ("Poids équipement (kg)", entry.get("struct_requirements_equipment_weight", "")),
                                ("Planéité du plancher",
                                 bool_to_oui_non(entry.get("struct_requirements_floor_flatness"))),
                                (
                                    "Présence de caniveau",
                                    bool_to_oui_non(entry.get("struct_requirements_ditch_gutter"))),
                                ("Sensibilité à l’acier",
                                 bool_to_oui_non(entry.get("struct_requirements_steel_sensitivity"))),
                                ("Autres équipements lourds", entry.get("struct_requirements_equipment_other", "")),
                                ("Sensibilité aux vibrations",
                                 bool_to_oui_non(entry.get("struct_requirements_vibrations_sensitivity"))),
                                ("Vibrations max (µm/s)", entry.get("struct_requirements_max_vibrations", "")),
                                ("Commentaire", entry.get("struct_requirements_commentary", ""))
                            ]

                            for label, value in fields:
                                value_clean = clean_text(str(value))
                                font_size = auto_font_size(pdf, value_clean, 120)
                                pdf.set_font("DejaVu", size=font_size)
                                pdf.cell(60, 8, f"{label} :", ln=0)
                                pdf.cell(120, 8, value_clean, ln=1)

                            pdf.ln(5)

                    elif table_name == "risk_elements":
                        for entry in table_data:
                            # Define labels for each set
                            risk_general_labels = {
                                "NA": "Aucun",
                                "concentrated_acids": "Acides concentrés",
                                "concentrated_base": "Bases concentrées",
                                "water_air_reactive": "Réactifs eau/air",
                                "radioactive": "Radioactifs"
                            }

                            risk_bio_labels = {
                                "NA": "Aucun",
                                "biological_products": "Produits biologiques",
                                "pathogens_humans": "Pathogènes humains",
                                "pathogens_animals": "Pathogènes animaux"
                            }

                            risk_gas_labels = {
                                "NA": "Aucun",
                                "gas_cylinders": "Bonbonnes de gaz",
                                "important_qty": "Quantité importante",
                                "toxic_gas": "Gaz toxique"
                            }

                            risk_liq_labels = {
                                "NA": "Aucun",
                                "flammable": "Liquide inflammable",
                                "important_qty": "Quantité importante",
                                "cryogenic": "Cryogénique"
                            }

                            risk_other_labels = {
                                "NA": "Aucun",
                                "lasers": "Lasers",
                                "animals": "Animaux"
                            }

                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Général :", ln=1)
                            pdf.set_font("DejaVu", size=10)

                            general_set = entry.get("risk_elements_general") or ""

                            checked = general_set.split(',') if isinstance(general_set, str) else list(general_set)

                            draw_checkbox_row(pdf, risk_general_labels.values(),
                                              [risk_general_labels[k] for k in checked if k in risk_general_labels])

                            pdf.cell(60, 8, "Détails radioactifs :", ln=0)
                            pdf.multi_cell(0, 8, clean_text(entry.get("risk_elements_general_radioactive", "")))

                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Biologique :", ln=1)
                            pdf.set_font("DejaVu", size=10)

                            bio_set = entry.get("risk_elements_biological") or ""

                            checked = bio_set.split(',') if isinstance(bio_set, str) else list(bio_set)
                            draw_checkbox_row(pdf, risk_bio_labels.values(),
                                              [risk_bio_labels[k] for k in checked if k in risk_bio_labels])
                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Gaz :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            gas_set = entry.get("risk_elements_gas") or ""
                            checked = gas_set.split(',') if isinstance(gas_set, str) else list(gas_set)
                            draw_checkbox_row(pdf, risk_gas_labels.values(),
                                              [risk_gas_labels[k] for k in checked if k in risk_gas_labels])
                            pdf.cell(60, 8, "Qté gaz :", ln=0)
                            pdf.cell(60, 8, clean_text(entry.get("risk_elements_gas_qty", "")), ln=1)
                            pdf.cell(60, 8, "Gaz toxique :", ln=0)
                            pdf.cell(60, 8, clean_text(entry.get("risk_elements_gas_toxic_gas", "")), ln=1)
                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Liquides :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            liq_set = entry.get("risk_elements_liquids") or ""
                            checked = liq_set.split(',') if isinstance(liq_set, str) else list(liq_set)
                            draw_checkbox_row(pdf, risk_liq_labels.values(),
                                              [risk_liq_labels[k] for k in checked if k in risk_liq_labels])
                            pdf.cell(60, 8, "Qté liquides :", ln=0)
                            pdf.cell(60, 8, clean_text(entry.get("risk_elements_liquids_qty", "")), ln=1)
                            pdf.cell(60, 8, "Liquides cryogéniques :", ln=0)
                            pdf.cell(60, 8, clean_text(entry.get("risk_elements_liquids_cryogenic", "")), ln=1)
                            pdf.ln(2)
                            pdf.set_font("DejaVu", "B", 10)
                            pdf.cell(0, 8, "Autres :", ln=1)
                            pdf.set_font("DejaVu", size=10)
                            other_set = entry.get("risk_elements_other") or ""
                            checked = other_set.split(',') if isinstance(other_set, str) else list(other_set)
                            draw_checkbox_row(pdf, risk_other_labels.values(),
                                              [risk_other_labels[k] for k in checked if k in risk_other_labels])
                            pdf.cell(60, 8, "Produits chimiques :", ln=0)
                            pdf.multi_cell(0, 8, clean_text(entry.get("risk_elements_chemical_products", "")))
                            pdf.ln(2)
                            pdf.cell(60, 8, "Commentaire :", ln=0)
                            pdf.multi_cell(0, 8, clean_text(entry.get("risk_elements_commentary", "")))
                            pdf.ln(5)

                    elif table_name == "ventilation_cvac":
                        for entry in table_data:
                            fields = [
                                ("Type de zone de soins", entry.get("ventilation_care_area_type", "")),
                                ("Ventilation", entry.get("ventilation", "")),
                                ("Mécanique spéciale", entry.get("ventilation_special_mechanics", "")),
                                ("Extraction spécifique", entry.get("ventilation_specific_exhaust", "")),
                                ("Pression relative de la salle",
                                 entry.get("ventilation_relative_room_pressure", "")),
                                ("Pressurisation", entry.get("ventilation_pressurization", "")),
                                ("Paramètres environnementaux",
                                 entry.get("ventilation_environmental_parameters", "")),
                                ("Commentaire", entry.get("ventilation_commentary", ""))
                            ]

                            for label, value in fields:
                                value_clean = clean_text(str(value))
                                font_size = auto_font_size(pdf, value_clean, 120)
                                pdf.set_font("DejaVu", size=font_size)
                                pdf.cell(60, 8, f"{label} :", ln=0)
                                pdf.cell(120, 8, value_clean, ln=1)

                            pdf.ln(5)

                    elif table_name == "electricity":
                        for entry in table_data:
                            fields = [
                                ("Type de zone de soins", entry.get("electricity_care_area_type", "")),
                                ("Détection fumée/incendie", entry.get("electricity_smoke_fire_detection", "")),
                                ("Équipement spécial", entry.get("electricity_special_equipment", "")),
                                ("Type d'éclairage", entry.get("electricity_lighting_type", "")),
                                ("Niveau d’éclairement", entry.get("electricity_lighting_level", "")),
                                ("Contrôle de l’éclairage", entry.get("electricity_lighting_control", "")),
                                ("Température de couleur", entry.get("color_temperature", "")),
                                ("Éclairage (détails)", entry.get("electricity_lighting", "")),
                                ("Commentaire", entry.get("electricity_commentary", ""))
                            ]

                            for label, value in fields:
                                value_clean = clean_text(str(value))
                                font_size = auto_font_size(pdf, value_clean, 120)
                                pdf.set_font("DejaVu", size=font_size)
                                pdf.cell(60, 8, f"{label} :", ln=0)
                                pdf.cell(120, 8, value_clean, ln=1)

                            pdf.ln(5)

                    elif table_name in special_tables:
                        for entry in table_data:
                            for key, val in entry.items():
                                if key.endswith('_id') or key == 'room_id':
                                    continue
                                label = clean_text(key.replace('_', ' ').capitalize())
                                val_clean = clean_text(val)
                                font_size = auto_font_size(pdf, val_clean, 120)
                                pdf.set_font("DejaVu", size=font_size)
                                pdf.cell(60, 8, f"{label} :", border=0)
                                pdf.cell(120, 8, val_clean, border=0, ln=True)
                            pdf.ln(3)

                    else:
                        headers = ["Catégorie", "Numéro", "Nom", "Quantité"]
                        keys = ["category", "number", "name", "quantity"]
                        col_widths = [50, 30, 60, 30]

                        pdf.set_font("DejaVu", "B", size=10)
                        for i, header in enumerate(headers):
                            pdf.cell(col_widths[i], 8, header, border=1)
                        pdf.ln()

                        pdf.set_font("DejaVu", size=10)
                        for entry in table_data:
                            for i, key_suffix in enumerate(keys):
                                field = f"{table_name}_{key_suffix}"
                                val = clean_text(entry.get(field, ""))
                                font_size = auto_font_size(pdf, val, col_widths[i])
                                pdf.set_font("DejaVu", size=font_size)
                                pdf.cell(col_widths[i], 8, val, border=1)
                            pdf.ln()
                        pdf.ln(5)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name
