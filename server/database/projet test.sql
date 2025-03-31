USE SPACELOGIC_7e19d0760b1a11f0ac899652d5389648;

INSERT INTO rooms (program_number, name, description, sector, functional_unit, level, planned_area) VALUES
    -- 🔹 Bloc Salles de Chirurgie
    ("101", "Salle de chirugie 101", "Salle de chirugie 101", "1", "1", "1", 50),
    ("102", "Salle de chirugie 102", "Salle de chirugie 102, utilisation alternative", "1", "1", "1", 50),
    ("103", "Salle de chirurgie 103", "Salle de chirurgie spécialisée", "1", "1", "2", 55),
    ("104", "Salle de chirurgie 104", "Bloc opératoire avancé", "1", "1", "3", 60),
    ("105", "Salle de chirurgie 105", "Salle pour chirurgie orthopédique", "1", "1", "4", 70),
    ("106", "Salle de chirurgie 106", "Chirurgie cardiaque et vasculaire", "1", "1", "5", 80),
    ("107", "Salle de chirurgie 107", "Salle de chirurgie ophtalmologique", "1", "1", "6", 50),

    -- 🔹 Bloc Consultations
    ("201", "Consultation ORL 201", "Salle de consultation en oto-rhino-laryngologie", "2", "2", "1", 30),
    ("202", "Consultation pédiatrie 202", "Salle de consultation pédiatrique", "2", "2", "2", 35),
    ("203", "Consultation cardiologie 203", "Salle de consultation cardiologique", "2", "2", "3", 40),
    ("204", "Consultation dermatologie 204", "Salle pour consultations dermatologiques", "2", "2", "4", 32),
    ("205", "Consultation neurologie 205", "Salle de consultation neurologique", "2", "2", "5", 38),

    -- 🔹 Bloc Urgences
    ("301", "Salle de soins urgences 301", "Salle de soins pour les urgences", "3", "3", "1", 50),
    ("302", "Salle de triage urgences 302", "Salle pour évaluation des patients aux urgences", "3", "3", "1", 45),
    ("303", "Salle de stabilisation 303", "Salle pour stabilisation des cas critiques", "3", "3", "2", 60),
    ("304", "Unité de soins intensifs 304", "Salle pour patients sous surveillance continue", "3", "3", "2", 80),
    ("305", "Salle de réanimation 305", "Salle équipée pour réanimations avancées", "3", "3", "3", 70),

    -- 🔹 Bloc Hospitalisation
    ("401", "Chambre patient 401", "Chambre standard pour hospitalisation", "4", "4", "1", 25),
    ("402", "Chambre VIP 402", "Chambre VIP pour hospitalisation", "4", "4", "2", 40),
    ("403", "Chambre double 403", "Chambre pour deux patients", "4", "4", "3", 35),
    ("404", "Unité de soins palliatifs 404", "Salle dédiée aux soins palliatifs", "4", "4", "4", 60),
    ("405", "Salle d'isolement 405", "Salle d'isolement pour maladies contagieuses", "4", "4", "5", 50),

    -- 🔹 Bloc Salles d'Imagerie Médicale
    ("501", "Salle de radiologie 501", "Salle équipée pour radiographies", "1", "5", "1", 50),
    ("502", "Salle IRM 502", "Salle équipée pour imagerie par résonance magnétique", "1", "5", "2", 70),
    ("503", "Salle scanner 503", "Salle avec scanner haute définition", "1", "5", "3", 65),
    ("504", "Salle échographie 504", "Salle équipée pour échographies", "1", "5", "4", 40),
    ("505", "Salle mammographie 505", "Salle spécialisée pour mammographies", "1", "5", "5", 45),

    -- 🔹 Bloc Rééducation et Réadaptation
    ("601", "Salle de kinésithérapie 601", "Salle pour rééducation physique", "2", "6", "1", 80),
    ("602", "Salle d'ergothérapie 602", "Salle pour rééducation cognitive et motrice", "2", "6", "2", 70),
    ("603", "Salle d'exercices 603", "Salle avec équipements pour réadaptation", "2", "6", "3", 90),
    ("604", "Salle de physiothérapie 604", "Salle pour thérapie physique avancée", "2", "6", "4", 85),

    -- 🔹 Bloc Administratif et Support
    ("701", "Bureau médecin chef 701", "Bureau du médecin chef", "3", "7", "1", 20),
    ("702", "Bureau directeur 702", "Bureau du directeur de l'hôpital", "3", "7", "2", 25),
    ("703", "Salle de réunion 703", "Salle pour réunions médicales et administratives", "3", "7", "3", 50),
    ("704", "Secrétariat médical 704", "Secrétariat pour prise de rendez-vous", "3", "7", "4", 30),
    ("705", "Salle de formation 705", "Salle pour formations du personnel médical", "3", "7", "5", 60),

    -- 🔹 Bloc Pharmacie et Stock
    ("801", "Pharmacie centrale 801", "Salle de stockage des médicaments", "4", "8", "1", 80),
    ("802", "Stock matériel médical 802", "Salle de stockage du matériel médical", "4", "8", "2", 100),
    ("803", "Salle de préparation 803", "Salle pour préparation des médicaments", "4", "8", "3", 50),

    -- 🔹 Bloc Laboratoire et Analyses
    ("901", "Laboratoire analyses médicales 901", "Salle d'analyses sanguines et biochimiques", "1", "9", "1", 80),
    ("902", "Laboratoire microbiologie 902", "Salle d'analyses microbiologiques", "1", "9", "2", 70),
    ("903", "Laboratoire pathologie 903", "Salle pour analyses histologiques", "1", "9", "3", 60),

    -- 🔹 Bloc Services Générals
    ("1001", "Cafétéria 1001", "Cafétéria pour les patients et le personnel", "4", "10", "1", 120),
    ("1002", "Salle de repos personnel 1002", "Salle de détente pour le personnel", "4", "10", "2", 50),
    ("1003", "Salle d'attente 1003", "Salle d'attente pour les familles et visiteurs", "4", "10", "3", 80);

INSERT INTO interior_fenestration (
    interior_fenestration_id, room_id,
    interior_fenestration_category, interior_fenestration_number,
    interior_fenestration_name, interior_fenestration_commentary,
    interior_fenestration_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Fenêtre intérieure fixe'
        WHEN 2 THEN 'Fenêtre avec stores intégrés'
        WHEN 3 THEN 'Fenêtre coulissante'
        WHEN 4 THEN 'Fenêtre vitrée avec cadre en aluminium'
    END,
    CONCAT('IF', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),  -- Numéro de fenêtre aléatoire ex: IF0123
    CONCAT('Fenestration intérieure pour ', r.name),
    'Fenêtre en verre sécurisée pour séparation de pièces',
    FLOOR(1 + RAND() * 3)  -- Quantité entre 1 et 3
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) AS a;


INSERT INTO exterior_fenestration (
    exterior_fenestration_id, room_id,
    exterior_fenestration_category, exterior_fenestration_number,
    exterior_fenestration_name, exterior_fenestration_commentary,
    exterior_fenestration_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Fenêtre fixe'
        WHEN 2 THEN 'Fenêtre battante'
        WHEN 3 THEN 'Baie vitrée'
        WHEN 4 THEN 'Fenêtre coulissante'
    END,
    CONCAT('EF', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Fenestration extérieure pour ', r.name),
    'Fenêtre installée pour une bonne isolation thermique',
    FLOOR(1 + RAND() * 4)  -- Quantité entre 1 et 4
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) AS b;



INSERT INTO finishes (
    finishes_id, room_id,
    finishes_category, finishes_number,
    finishes_name, finishes_commentary,
    finishes_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Peinture'
        WHEN 2 THEN 'Papier peint'
        WHEN 3 THEN 'Revêtement en bois'
    END,
    CONCAT('FIN', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Finition de ', r.name),
    'Revêtement intérieur esthétique et fonctionnel',
    FLOOR(1 + RAND() * 2)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2) AS d;



INSERT INTO doors (
    doors_id, room_id,
    doors_category, doors_number,
    doors_name, doors_commentary,
    doors_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Porte battante'
        WHEN 2 THEN 'Porte coulissante'
        WHEN 3 THEN 'Porte hermétique'
    END,
    CONCAT('D', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Porte de ', r.name),
    'Porte sécurisée avec isolation acoustique',
    FLOOR(1 + RAND() * 2)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) AS e;



INSERT INTO built_in_fournitures (
    built_in_fournitures_id, room_id,
    built_in_fournitures_category, built_in_fournitures_number,
    built_in_fournitures_name, built_in_fournitures_commentary,
    built_in_fournitures_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Placard mural'
        WHEN 2 THEN 'Étagères intégrées'
        WHEN 3 THEN 'Banque d’armoires'
        WHEN 4 THEN 'Table de soins'
    END,
    CONCAT('BI', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Mobilier intégré de ', r.name),
    'Mobilier conçu pour maximiser l’espace',
    FLOOR(1 + RAND() * 3)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2) AS f;



INSERT INTO accessories (
    accessories_id, room_id,
    accessories_category, accessories_number,
    accessories_name, accessories_commentary,
    accessories_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Support mural'
        WHEN 2 THEN 'Distributeur de savon'
        WHEN 3 THEN 'Porte-serviettes'
    END,
    CONCAT('ACC', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Accessoire pour ', r.name),
    'Accessoire fonctionnel pour amélioration du confort',
    FLOOR(1 + RAND() * 5)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2) AS g;



INSERT INTO plumbings (
    plumbings_id, room_id,
    plumbings_category, plumbings_number,
    plumbings_name, plumbings_commentary,
    plumbings_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Évier médical'
        WHEN 2 THEN 'Douche'
        WHEN 3 THEN 'Toilette'
        WHEN 4 THEN 'Robinet automatique'
    END,
    CONCAT('PL', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Plomberie pour ', r.name),
    'Installation respectant les normes sanitaires',
    FLOOR(1 + RAND() * 2)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) AS h;



INSERT INTO fire_protection (
    fire_protection_id, room_id,
    fire_protection_category, fire_protection_number,
    fire_protection_name, fire_protection_commentary,
    fire_protection_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Extincteur'
        WHEN 2 THEN 'Détecteur de fumée'
        WHEN 3 THEN 'Système d’alarme incendie'
        WHEN 4 THEN 'Porte coupe-feu'
    END,
    CONCAT('FP', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Équipement incendie de ', r.name),
    'Dispositif essentiel pour la sécurité incendie',
    FLOOR(1 + RAND() * 3)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2) AS i;



INSERT INTO lighting (
    lighting_id, room_id,
    lighting_category, lighting_number,
    lighting_name, lighting_commentary,
    lighting_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Lumière LED'
        WHEN 2 THEN 'Lustre suspendu'
        WHEN 3 THEN 'Spot encastré'
    END,
    CONCAT('LT', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Éclairage de ', r.name),
    'Éclairage optimisé pour une bonne visibilité',
    FLOOR(2 + RAND() * 5)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2) AS j;



INSERT INTO electrical_outlets (
    electrical_outlets_id, room_id,
    electrical_outlets_category, electrical_outlets_number,
    electrical_outlets_name, electrical_outlets_commentary,
    electrical_outlets_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    r.id,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Prise standard'
        WHEN 2 THEN 'Prise médicale'
        WHEN 3 THEN 'Prise USB intégrée'
    END,
    CONCAT('EO', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Prise électrique dans ', r.name),
    'Prise conforme aux normes électriques hospitalières',
    FLOOR(2 + RAND() * 6)
FROM rooms r
JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) AS k;



INSERT INTO communication_security (
    communication_security_id, room_id,
    communication_security_category, communication_security_number,
    communication_security_name, communication_security_commentary,
    communication_security_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Interphone médical'
        WHEN 2 THEN 'Caméra de surveillance'
        WHEN 3 THEN 'Système d’appel infirmier'
        WHEN 4 THEN 'Badge d’accès sécurisé'
    END,
    CONCAT('CS', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Système de sécurité pour ', name),
    'Système avancé pour la communication et la surveillance',
    FLOOR(1 + RAND() * 4)
FROM rooms
ORDER BY RAND()
LIMIT 90;


INSERT INTO medical_equipment (
    medical_equipment_id, room_id,
    medical_equipment_category, medical_equipment_number,
    medical_equipment_name, medical_equipment_commentary,
    medical_equipment_quantity
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN 'Moniteur cardiaque'
        WHEN 2 THEN 'Appareil d’oxygénothérapie'
        WHEN 3 THEN 'Table d’examen'
        WHEN 4 THEN 'Défibrillateur'
    END,
    CONCAT('ME', LPAD(FLOOR(RAND() * 9999) + 1, 4, '0')),
    CONCAT('Équipement médical pour ', name),
    'Dispositif essentiel pour le suivi des patients',
    FLOOR(1 + RAND() * 2)
FROM rooms
ORDER BY RAND()
LIMIT 80;


INSERT INTO functionality (
    functionality_id, room_id,
    functionality_occupants_number, functionality_desk_number,
    functionality_lab_number, functionality_schedule,
    functionality_access, functionality_access_adj_room,
    functionality_access_other, functionality_consideration,
    functionality_consideration_other, functionality_description,
    functionality_proximity, functionality_commentary
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    FLOOR(1 + RAND() * 20),  -- Nombre d'occupants (1-20)
    FLOOR(1 + RAND() * 5),   -- Nombre de bureaux (1-5)
    FLOOR(RAND() * 3),       -- Nombre de laboratoires (0-2)
    CASE FLOOR(RAND() * 4) + 1
        WHEN 1 THEN '24h/24'
        WHEN 2 THEN '7h-19h'
        WHEN 3 THEN 'Jour et nuit'
        WHEN 4 THEN 'Selon besoins'
    END,
    -- 🔹 Générer aléatoirement entre 1 et 3 valeurs SET valides
    TRIM(BOTH ',' FROM CONCAT(
        CASE WHEN RAND() > 0.5 THEN 'client_access,' ELSE '' END,
        CASE WHEN RAND() > 0.5 THEN 'stretcher_access,' ELSE '' END,
        CASE WHEN RAND() > 0.5 THEN 'bed_access,' ELSE '' END,
        CASE WHEN RAND() > 0.5 THEN 'patients_access,' ELSE '' END,
        CASE WHEN RAND() > 0.5 THEN 'exterior_access,' ELSE '' END,
        CASE WHEN RAND() > 0.5 THEN 'hallway_access,' ELSE '' END,
        CASE WHEN RAND() > 0.5 THEN 'adj_room_access,' ELSE '' END,
        CASE WHEN RAND() > 0.7 THEN 'other' ELSE '' END
    )),
    'Accès à une salle adjacente',
    NULL,
    'sterile,vibrations_sensitivity',
    NULL,
    CONCAT('Fonctionnalité standard de ', name),
    'À proximité immédiate du bloc médical',
    'Aucun commentaire'
FROM rooms;


INSERT INTO arch_requirements (
    arch_requirements_id, room_id,
    arch_requirements_critic_length, arch_requirements_critic_width,
    arch_requirements_critic_height, arch_requirements_validation_req,
    arch_requirements_acoustic, arch_requirements_int_fenestration,
    arch_requirements_int_fen_adj_room, arch_requirements_int_fen_other,
    arch_requirements_ext_fenestration, arch_requirements_ext_fen_solar_blind,
    arch_requirements_ext_fen_opaque_blind, arch_requirements_commentary
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    5 + FLOOR(RAND() * 10),   -- Longueur critique (5-15m)
    3 + FLOOR(RAND() * 7),    -- Largeur critique (3-10m)
    2 + FLOOR(RAND() * 3),    -- Hauteur critique (2-5m)
    FLOOR(RAND() * 2),        -- Validation requise ou non
    FLOOR(30 + RAND() * 50),  -- Acoustique (30-80)
    CASE FLOOR(RAND() * 7) + 1  -- 🔹 Prend une valeur aléatoire dans le SET
        WHEN 1 THEN 'not_required'
        WHEN 2 THEN 'with_hallway'
        WHEN 3 THEN 'clear_glass'
        WHEN 4 THEN 'frosted_glass'
        WHEN 5 THEN 'semi_frosted_glass'
        WHEN 6 THEN 'one_way_glass'
        WHEN 7 THEN 'integrated_blind'
    END,
    'Vue sur couloir',
    NULL,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'not_required'
        WHEN 2 THEN 'required'
        WHEN 3 THEN 'frosted_glass'
    END,
    NULL,
    NULL,
    'Exigences architecturales adaptées à l’usage médical'
FROM rooms;



INSERT INTO struct_requirements (
    struct_requirements_id, room_id,
    struct_requirements_floor_overload_required, struct_requirements_overload,
    struct_requirements_equipment_weight, struct_requirements_floor_flatness,
    struct_requirements_ditch_gutter, struct_requirements_steel_sensitivity,
    struct_requirements_equipment_other, struct_requirements_vibrations_sensitivity,
    struct_requirements_max_vibrations, struct_requirements_commentary
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    FLOOR(RAND() * 2),  -- Besoin d'une surcharge (0 ou 1)
    FLOOR(100 + RAND() * 500),  -- Surcharge (100-600kg/m²)
    FLOOR(50 + RAND() * 300),   -- Poids de l’équipement (50-350kg)
    FLOOR(RAND() * 2),  -- Planéité (0 ou 1)
    FLOOR(RAND() * 2),  -- Présence de rigole (0 ou 1)
    FLOOR(RAND() * 2),  -- Sensibilité acier (0 ou 1)
    'Équipements lourds',
    FLOOR(RAND() * 2),  -- Sensibilité vibrations (0 ou 1)
    FLOOR(1 + RAND() * 10),  -- Max vibrations (1-10Hz)
    'Commentaires structuraux adaptés à l’usage hospitalier'
FROM rooms;


INSERT INTO risk_elements (
    risk_elements_id, room_id,
    risk_elements_general, risk_elements_general_radioactive,
    risk_elements_biological, risk_elements_gas,
    risk_elements_gas_qty, risk_elements_gas_toxic_gas,
    risk_elements_liquids, risk_elements_liquids_qty,
    risk_elements_liquids_cryogenic, risk_elements_other,
    risk_elements_chemical_products, risk_elements_commentary
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    'NA', NULL,
    'NA', 'NA',
    NULL, NULL,
    'NA', NULL,
    NULL, 'NA',
    NULL, 'Aucun risque identifié'
FROM rooms;


INSERT INTO ventilation_cvac (
    ventilation_cvac_id, room_id,
    ventilation_care_area_type, ventilation,
    ventilation_special_mechanics, ventilation_specific_exhaust,
    ventilation_commentary, ventilation_relative_room_pressure,
    ventilation_pressurization, ventilation_environmental_parameters
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Standard'
        WHEN 2 THEN 'Soins intensifs'
        WHEN 3 THEN 'Bloc opératoire'
    END,
    'Système de renouvellement d’air centralisé',
    'Filtration HEPA',
    'Évacuation spécifique pour contaminants',
    'Ventilation adaptée à la configuration de la pièce',
    CASE FLOOR(RAND() * 3) + 1
        WHEN 1 THEN 'Positive'
        WHEN 2 THEN 'Négative'
        WHEN 3 THEN 'Neutre'
    END,
    'Contrôle automatique',
    'Régulation de température et humidité'
FROM rooms;


INSERT INTO electricity (
    electricity_id, room_id,
    electricity_care_area_type, electricity_smoke_fire_detection,
    electricity_special_equipment, electricity_lighting_type,
    electricity_lighting_level, electricity_lighting_control,
    color_temperature, electricity_lighting, electricity_commentary
)
SELECT
    UUID_TO_BIN(UUID()),
    id,
    'Soins intensifs',
    'Détection incendie avancée',
    'Équipements de secours électriques',
    'LED haute intensité',
    'Niveau ajustable',
    'Commande tactile',
    '4500K',  -- Température de couleur
    'Éclairage optimisé pour activités médicales',
    'Conformité aux normes électriques hospitalières'
FROM rooms;

