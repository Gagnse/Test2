-- procedures to help retrieve historical changes
-- for entities in the project database

DELIMITER //

-- Procedure to get all historical changes for a specific entity
CREATE PROCEDURE get_entity_history(
    IN p_entity_type VARCHAR(50),
    IN p_entity_id BINARY(16)
)
BEGIN
    SELECT 
        BIN_TO_UUID(entity_id) AS entity_id,
        entity_type,
        change_type,
        change_date,
        version_number,
        BIN_TO_UUID(user_id) AS user_id,
        old_value,
        new_value
    FROM 
        historical_changes
    WHERE 
        entity_type = p_entity_type 
        AND entity_id = p_entity_id
    ORDER BY 
        change_date DESC, 
        CAST(version_number AS DECIMAL(10,1)) DESC;
END //

-- Procedure to get all historical changes for a specific room and all its related data
CREATE PROCEDURE get_room_history(
    IN p_room_id BINARY(16)
)
BEGIN
    -- Get room history
    SELECT 
        'Room' AS entity_category,
        BIN_TO_UUID(entity_id) AS entity_id,
        entity_type,
        change_type,
        change_date,
        version_number,
        BIN_TO_UUID(user_id) AS user_id,
        old_value,
        new_value
    FROM 
        historical_changes
    WHERE 
        entity_type = 'room' 
        AND entity_id = p_room_id
    
    UNION ALL
    
    -- Get history for all related entities (functionality, arch_requirements, etc.)
    SELECT 
        entity_type AS entity_category,
        BIN_TO_UUID(hc.entity_id) AS entity_id,
        hc.entity_type,
        hc.change_type,
        hc.change_date,
        hc.version_number,
        BIN_TO_UUID(hc.user_id) AS user_id,
        hc.old_value,
        hc.new_value
    FROM 
        historical_changes hc
    WHERE 
        (
            (hc.entity_type = 'functionality' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'arch_requirements' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'risk_elements' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'ventilation_cvac' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'electricity' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'struct_requirements' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
        )
    
    ORDER BY 
        change_date DESC, 
        entity_category,
        CAST(version_number AS DECIMAL(10,1)) DESC;
END //

-- Function to get the user's name from ID
CREATE FUNCTION get_user_name(p_user_id BINARY(16))
RETURNS VARCHAR(255)
READS SQL DATA
BEGIN
    DECLARE v_user_name VARCHAR(255);
    
    -- Query the users database to get the user's name
    -- Note: This requires appropriate privileges across databases
    SELECT CONCAT(first_name, ' ', last_name) INTO v_user_name
    FROM SPACELOGIC_ADMIN_DB.users 
    WHERE id = p_user_id;
    
    IF v_user_name IS NULL THEN
        RETURN 'Unknown User';
    END IF;
    
    RETURN v_user_name;
END //

-- Procedure to get a formatted change history report for a room
CREATE PROCEDURE get_room_history_report(
    IN p_room_id BINARY(16)
)
BEGIN
    -- Get the room name
    DECLARE v_room_name VARCHAR(100);
    
    SELECT name INTO v_room_name FROM rooms WHERE id = p_room_id;
    
    -- Show header
    SELECT CONCAT('History Report for Room: ', v_room_name, ' (', BIN_TO_UUID(p_room_id), ')') AS report_header;
    
    -- Get all changes sorted by date
    SELECT 
        change_date,
        entity_type,
        change_type,
        version_number,
        get_user_name(user_id) AS modified_by,
        CASE
            WHEN change_type = 'INSERT' THEN 'Created'
            WHEN change_type = 'UPDATE' THEN 
                CONCAT('Changed: ', 
                    SUBSTRING_INDEX(
                        GROUP_CONCAT(
                            CASE 
                                WHEN JSON_KEYS(old_value) = JSON_KEYS(new_value) THEN
                                    CONCAT(
                                        JSON_KEYS(changed_fields), 
                                        ' from ', 
                                        JSON_EXTRACT(old_value, CONCAT('$.', JSON_KEYS(changed_fields))),
                                        ' to ',
                                        JSON_EXTRACT(new_value, CONCAT('$.', JSON_KEYS(changed_fields)))
                                    )
                                ELSE 'Multiple fields'
                            END
                            SEPARATOR ', '
                        ), 
                        ',', 2
                    ),
                    IF(LENGTH(GROUP_CONCAT(CASE WHEN JSON_KEYS(changed_fields) IS NULL THEN '' ELSE JSON_KEYS(changed_fields) END SEPARATOR ', ')) > 50, '...', '')
                )
            WHEN change_type = 'DELETE' THEN 'Deleted'
        END AS change_description
    FROM (
        SELECT 
            hc.entity_type,
            hc.change_type,
            hc.change_date,
            hc.version_number,
            hc.user_id,
            hc.old_value,
            hc.new_value,
            -- Extract changed fields (for UPDATE operations)
            CASE 
                WHEN hc.change_type = 'UPDATE' THEN 
                    JSON_EXTRACT(hc.new_value, '$.commentary') 
                ELSE NULL
            END AS changed_fields
        FROM 
            historical_changes hc
        WHERE 
            (hc.entity_type = 'room' AND hc.entity_id = p_room_id)
            OR
            (hc.entity_type = 'functionality' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'arch_requirements' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'risk_elements' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'ventilation_cvac' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'electricity' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
            OR
            (hc.entity_type = 'struct_requirements' AND 
             JSON_EXTRACT(IFNULL(hc.old_value, hc.new_value), '$.room_id') = BIN_TO_UUID(p_room_id))
    ) AS changes
    GROUP BY
        change_date,
        entity_type,
        change_type,
        version_number,
        user_id
    ORDER BY 
        change_date DESC,
        entity_type,
        version_number DESC;
END //

DELIMITER ;