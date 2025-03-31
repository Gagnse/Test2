-- Each table has 3 triggers: INSERT, UPDATE, DELETE
-- All changes are tracked in the historical_changes table

DELIMITER //

-- ============================== ROOM TRIGGERS ==============================
-- INSERT Trigger for rooms
CREATE TRIGGER IF NOT EXISTS rooms_after_insert
AFTER INSERT ON rooms
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'room',
        NEW.id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'program_number', NEW.program_number,
            'name', NEW.name,
            'description', NEW.description,
            'sector', NEW.sector,
            'functional_unit', NEW.functional_unit,
            'level', NEW.level,
            'planned_area', NEW.planned_area
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for rooms
CREATE TRIGGER IF NOT EXISTS rooms_after_update
AFTER UPDATE ON rooms
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE changes JSON;
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Build JSON of changes
    SET changes = JSON_OBJECT();

    IF NEW.program_number != OLD.program_number THEN
        SET changes = JSON_SET(changes, '$.program_number', JSON_OBJECT('old', OLD.program_number, 'new', NEW.program_number));
    END IF;

    IF NEW.name != OLD.name THEN
        SET changes = JSON_SET(changes, '$.name', JSON_OBJECT('old', OLD.name, 'new', NEW.name));
    END IF;

    IF (NEW.description IS NOT NULL AND OLD.description IS NOT NULL AND NEW.description != OLD.description)
       OR (NEW.description IS NULL AND OLD.description IS NOT NULL)
       OR (NEW.description IS NOT NULL AND OLD.description IS NULL) THEN
        SET changes = JSON_SET(changes, '$.description', JSON_OBJECT(
            'old', IFNULL(OLD.description, 'NULL'),
            'new', IFNULL(NEW.description, 'NULL')
        ));
    END IF;

    IF (NEW.sector IS NOT NULL AND OLD.sector IS NOT NULL AND NEW.sector != OLD.sector)
       OR (NEW.sector IS NULL AND OLD.sector IS NOT NULL)
       OR (NEW.sector IS NOT NULL AND OLD.sector IS NULL) THEN
        SET changes = JSON_SET(changes, '$.sector', JSON_OBJECT(
            'old', IFNULL(OLD.sector, 'NULL'),
            'new', IFNULL(NEW.sector, 'NULL')
        ));
    END IF;

    IF (NEW.functional_unit IS NOT NULL AND OLD.functional_unit IS NOT NULL AND NEW.functional_unit != OLD.functional_unit)
       OR (NEW.functional_unit IS NULL AND OLD.functional_unit IS NOT NULL)
       OR (NEW.functional_unit IS NOT NULL AND OLD.functional_unit IS NULL) THEN
        SET changes = JSON_SET(changes, '$.functional_unit', JSON_OBJECT(
            'old', IFNULL(OLD.functional_unit, 'NULL'),
            'new', IFNULL(NEW.functional_unit, 'NULL')
        ));
    END IF;

    IF (NEW.level IS NOT NULL AND OLD.level IS NOT NULL AND NEW.level != OLD.level)
       OR (NEW.level IS NULL AND OLD.level IS NOT NULL)
       OR (NEW.level IS NOT NULL AND OLD.level IS NULL) THEN
        SET changes = JSON_SET(changes, '$.level', JSON_OBJECT(
            'old', IFNULL(OLD.level, 'NULL'),
            'new', IFNULL(NEW.level, 'NULL')
        ));
    END IF;

    IF NEW.planned_area != OLD.planned_area THEN
        SET changes = JSON_SET(changes, '$.planned_area', JSON_OBJECT('old', OLD.planned_area, 'new', NEW.planned_area));
    END IF;

    -- Only insert if changes were made
    IF JSON_LENGTH(changes) > 0 THEN
        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'room' AND entity_id = NEW.id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'room',
            NEW.id,
            'UPDATE',
            JSON_OBJECT(
                'program_number', OLD.program_number,
                'name', OLD.name,
                'description', OLD.description,
                'sector', OLD.sector,
                'functional_unit', OLD.functional_unit,
                'level', OLD.level,
                'planned_area', OLD.planned_area
            ),
            JSON_OBJECT(
                'program_number', NEW.program_number,
                'name', NEW.name,
                'description', NEW.description,
                'sector', NEW.sector,
                'functional_unit', NEW.functional_unit,
                'level', NEW.level,
                'planned_area', NEW.planned_area
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for rooms
CREATE TRIGGER IF NOT EXISTS rooms_after_delete
AFTER DELETE ON rooms
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'room' AND entity_id = OLD.id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'room',
        OLD.id,
        'DELETE',
        JSON_OBJECT(
            'program_number', OLD.program_number,
            'name', OLD.name,
            'description', OLD.description,
            'sector', OLD.sector,
            'functional_unit', OLD.functional_unit,
            'level', OLD.level,
            'planned_area', OLD.planned_area
        ),
        NULL,
        current_version,
        current_user_id
    );
END //

-- ============================== ELECTRICITY TRIGGERS ==============================
-- INSERT Trigger for electricity
CREATE TRIGGER IF NOT EXISTS electricity_after_insert
AFTER INSERT ON electricity
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'electricity',
        NEW.electricity_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(NEW.room_id),
            'care_area_type', NEW.electricity_care_area_type,
            'smoke_fire_detection', NEW.electricity_smoke_fire_detection,
            'special_equipment', NEW.electricity_special_equipment,
            'lighting_type', NEW.electricity_lighting_type,
            'lighting_level', NEW.electricity_lighting_level,
            'lighting_control', NEW.electricity_lighting_control,
            'color_temperature', NEW.color_temperature,
            'lighting', NEW.electricity_lighting,
            'commentary', NEW.electricity_commentary
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for electricity
CREATE TRIGGER IF NOT EXISTS electricity_after_update
AFTER UPDATE ON electricity
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Check if any field has changed
    IF NOT (NEW.electricity_care_area_type <=> OLD.electricity_care_area_type) OR
       NOT (NEW.electricity_smoke_fire_detection <=> OLD.electricity_smoke_fire_detection) OR
       NOT (NEW.electricity_special_equipment <=> OLD.electricity_special_equipment) OR
       NOT (NEW.electricity_lighting_type <=> OLD.electricity_lighting_type) OR
       NOT (NEW.electricity_lighting_level <=> OLD.electricity_lighting_level) OR
       NOT (NEW.electricity_lighting_control <=> OLD.electricity_lighting_control) OR
       NOT (NEW.color_temperature <=> OLD.color_temperature) OR
       NOT (NEW.electricity_lighting <=> OLD.electricity_lighting) OR
       NOT (NEW.electricity_commentary <=> OLD.electricity_commentary) THEN

        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'electricity' AND entity_id = NEW.electricity_id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'electricity',
            NEW.electricity_id,
            'UPDATE',
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(OLD.room_id),
                'care_area_type', OLD.electricity_care_area_type,
                'smoke_fire_detection', OLD.electricity_smoke_fire_detection,
                'special_equipment', OLD.electricity_special_equipment,
                'lighting_type', OLD.electricity_lighting_type,
                'lighting_level', OLD.electricity_lighting_level,
                'lighting_control', OLD.electricity_lighting_control,
                'color_temperature', OLD.color_temperature,
                'lighting', OLD.electricity_lighting,
                'commentary', OLD.electricity_commentary
            ),
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(NEW.room_id),
                'care_area_type', NEW.electricity_care_area_type,
                'smoke_fire_detection', NEW.electricity_smoke_fire_detection,
                'special_equipment', NEW.electricity_special_equipment,
                'lighting_type', NEW.electricity_lighting_type,
                'lighting_level', NEW.electricity_lighting_level,
                'lighting_control', NEW.electricity_lighting_control,
                'color_temperature', NEW.color_temperature,
                'lighting', NEW.electricity_lighting,
                'commentary', NEW.electricity_commentary
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for electricity
CREATE TRIGGER IF NOT EXISTS electricity_after_delete
AFTER DELETE ON electricity
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'electricity' AND entity_id = OLD.electricity_id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'electricity',
        OLD.electricity_id,
        'DELETE',
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(OLD.room_id),
            'care_area_type', OLD.electricity_care_area_type,
            'smoke_fire_detection', OLD.electricity_smoke_fire_detection,
            'special_equipment', OLD.electricity_special_equipment,
            'lighting_type', OLD.electricity_lighting_type,
            'lighting_level', OLD.electricity_lighting_level,
            'lighting_control', OLD.electricity_lighting_control,
            'color_temperature', OLD.color_temperature,
            'lighting', OLD.electricity_lighting,
            'commentary', OLD.electricity_commentary
        ),
        NULL,
        current_version,
        current_user_id
    );
END //

-- ============================== STRUCT_REQUIREMENTS TRIGGERS ==============================
-- INSERT Trigger for struct_requirements
CREATE TRIGGER IF NOT EXISTS struct_requirements_after_insert
AFTER INSERT ON struct_requirements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'struct_requirements',
        NEW.struct_requirements_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(NEW.room_id),
            'floor_overload_required', NEW.struct_requirements_floor_overload_required,
            'overload', NEW.struct_requirements_overload,
            'equipment_weight', NEW.struct_requirements_equipment_weight,
            'floor_flatness', NEW.struct_requirements_floor_flatness,
            'ditch_gutter', NEW.struct_requirements_ditch_gutter,
            'steel_sensitivity', NEW.struct_requirements_steel_sensitivity,
            'equipment_other', NEW.struct_requirements_equipment_other,
            'vibrations_sensitivity', NEW.struct_requirements_vibrations_sensitivity,
            'max_vibrations', NEW.struct_requirements_max_vibrations,
            'commentary', NEW.struct_requirements_commentary
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for struct_requirements
CREATE TRIGGER IF NOT EXISTS struct_requirements_after_update
AFTER UPDATE ON struct_requirements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Check if any field has changed
    IF NOT (NEW.struct_requirements_floor_overload_required <=> OLD.struct_requirements_floor_overload_required) OR
       NOT (NEW.struct_requirements_overload <=> OLD.struct_requirements_overload) OR
       NOT (NEW.struct_requirements_equipment_weight <=> OLD.struct_requirements_equipment_weight) OR
       NOT (NEW.struct_requirements_floor_flatness <=> OLD.struct_requirements_floor_flatness) OR
       NOT (NEW.struct_requirements_ditch_gutter <=> OLD.struct_requirements_ditch_gutter) OR
       NOT (NEW.struct_requirements_steel_sensitivity <=> OLD.struct_requirements_steel_sensitivity) OR
       NOT (NEW.struct_requirements_equipment_other <=> OLD.struct_requirements_equipment_other) OR
       NOT (NEW.struct_requirements_vibrations_sensitivity <=> OLD.struct_requirements_vibrations_sensitivity) OR
       NOT (NEW.struct_requirements_max_vibrations <=> OLD.struct_requirements_max_vibrations) OR
       NOT (NEW.struct_requirements_commentary <=> OLD.struct_requirements_commentary) THEN

        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'struct_requirements' AND entity_id = NEW.struct_requirements_id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'struct_requirements',
            NEW.struct_requirements_id,
            'UPDATE',
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(OLD.room_id),
                'floor_overload_required', OLD.struct_requirements_floor_overload_required,
                'overload', OLD.struct_requirements_overload,
                'equipment_weight', OLD.struct_requirements_equipment_weight,
                'floor_flatness', OLD.struct_requirements_floor_flatness,
                'ditch_gutter', OLD.struct_requirements_ditch_gutter,
                'steel_sensitivity', OLD.struct_requirements_steel_sensitivity,
                'equipment_other', OLD.struct_requirements_equipment_other,
                'vibrations_sensitivity', OLD.struct_requirements_vibrations_sensitivity,
                'max_vibrations', OLD.struct_requirements_max_vibrations,
                'commentary', OLD.struct_requirements_commentary
            ),
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(NEW.room_id),
                'floor_overload_required', NEW.struct_requirements_floor_overload_required,
                'overload', NEW.struct_requirements_overload,
                'equipment_weight', NEW.struct_requirements_equipment_weight,
                'floor_flatness', NEW.struct_requirements_floor_flatness,
                'ditch_gutter', NEW.struct_requirements_ditch_gutter,
                'steel_sensitivity', NEW.struct_requirements_steel_sensitivity,
                'equipment_other', NEW.struct_requirements_equipment_other,
                'vibrations_sensitivity', NEW.struct_requirements_vibrations_sensitivity,
                'max_vibrations', NEW.struct_requirements_max_vibrations,
                'commentary', NEW.struct_requirements_commentary
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for struct_requirements
CREATE TRIGGER IF NOT EXISTS struct_requirements_after_delete
AFTER DELETE ON struct_requirements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'struct_requirements' AND entity_id = OLD.struct_requirements_id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'struct_requirements',
        OLD.struct_requirements_id,
        'DELETE',
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(OLD.room_id),
            'floor_overload_required', OLD.struct_requirements_floor_overload_required,
            'overload', OLD.struct_requirements_overload,
            'equipment_weight', OLD.struct_requirements_equipment_weight,
            'floor_flatness', OLD.struct_requirements_floor_flatness,
            'ditch_gutter', OLD.struct_requirements_ditch_gutter,
            'steel_sensitivity', OLD.struct_requirements_steel_sensitivity,
            'equipment_other', OLD.struct_requirements_equipment_other,
            'vibrations_sensitivity', OLD.struct_requirements_vibrations_sensitivity,
            'max_vibrations', OLD.struct_requirements_max_vibrations,
            'commentary', OLD.struct_requirements_commentary
        ),
        NULL,
        current_version,
        current_user_id
    );
END //

DELIMITER ;

-- ============================== FUNCTIONALITY TRIGGERS ==============================
-- INSERT Trigger for functionality
CREATE TRIGGER IF NOT EXISTS functionality_after_insert
AFTER INSERT ON functionality
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'functionality',
        NEW.functionality_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(NEW.room_id),
            'occupants_number', NEW.functionality_occupants_number,
            'desk_number', NEW.functionality_desk_number,
            'lab_number', NEW.functionality_lab_number,
            'schedule', NEW.functionality_schedule,
            'access', NEW.functionality_access,
            'description', NEW.functionality_description,
            'proximity', NEW.functionality_proximity,
            'commentary', NEW.functionality_commentary
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for functionality
CREATE TRIGGER IF NOT EXISTS functionality_after_update
AFTER UPDATE ON functionality
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Check if any important field has changed
    IF NEW.functionality_occupants_number != OLD.functionality_occupants_number OR
       NEW.functionality_desk_number != OLD.functionality_desk_number OR
       NEW.functionality_lab_number != OLD.functionality_lab_number OR
       NOT (NEW.functionality_schedule <=> OLD.functionality_schedule) OR
       NOT (NEW.functionality_access <=> OLD.functionality_access) OR
       NOT (NEW.functionality_description <=> OLD.functionality_description) OR
       NOT (NEW.functionality_proximity <=> OLD.functionality_proximity) OR
       NOT (NEW.functionality_commentary <=> OLD.functionality_commentary) THEN

        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'functionality' AND entity_id = NEW.functionality_id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'functionality',
            NEW.functionality_id,
            'UPDATE',
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(OLD.room_id),
                'occupants_number', OLD.functionality_occupants_number,
                'desk_number', OLD.functionality_desk_number,
                'lab_number', OLD.functionality_lab_number,
                'schedule', OLD.functionality_schedule,
                'access', OLD.functionality_access,
                'description', OLD.functionality_description,
                'proximity', OLD.functionality_proximity,
                'commentary', OLD.functionality_commentary
            ),
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(NEW.room_id),
                'occupants_number', NEW.functionality_occupants_number,
                'desk_number', NEW.functionality_desk_number,
                'lab_number', NEW.functionality_lab_number,
                'schedule', NEW.functionality_schedule,
                'access', NEW.functionality_access,
                'description', NEW.functionality_description,
                'proximity', NEW.functionality_proximity,
                'commentary', NEW.functionality_commentary
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for functionality
CREATE TRIGGER IF NOT EXISTS functionality_after_delete
AFTER DELETE ON functionality
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'functionality' AND entity_id = OLD.functionality_id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'functionality',
        OLD.functionality_id,
        'DELETE',
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(OLD.room_id),
            'occupants_number', OLD.functionality_occupants_number,
            'desk_number', OLD.functionality_desk_number,
            'lab_number', OLD.functionality_lab_number,
            'schedule', OLD.functionality_schedule,
            'access', OLD.functionality_access,
            'description', OLD.functionality_description,
            'proximity', OLD.functionality_proximity,
            'commentary', OLD.functionality_commentary
        ),
        NULL,
        current_version,
        current_user_id
    );
END //

-- ============================== ARCH_REQUIREMENTS TRIGGERS ==============================
-- INSERT Trigger for arch_requirements
CREATE TRIGGER IF NOT EXISTS arch_requirements_after_insert
AFTER INSERT ON arch_requirements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'arch_requirements',
        NEW.arch_requirements_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(NEW.room_id),
            'critic_length', NEW.arch_requirements_critic_length,
            'critic_width', NEW.arch_requirements_critic_width,
            'critic_height', NEW.arch_requirements_critic_height,
            'validation_req', NEW.arch_requirements_validation_req,
            'acoustic', NEW.arch_requirements_acoustic,
            'int_fenestration', NEW.arch_requirements_int_fenestration,
            'ext_fenestration', NEW.arch_requirements_ext_fenestration,
            'commentary', NEW.arch_requirements_commentary
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for arch_requirements
CREATE TRIGGER IF NOT EXISTS arch_requirements_after_update
AFTER UPDATE ON arch_requirements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Check if any field has changed
    IF NEW.arch_requirements_critic_length != OLD.arch_requirements_critic_length OR
       NEW.arch_requirements_critic_width != OLD.arch_requirements_critic_width OR
       NEW.arch_requirements_critic_height != OLD.arch_requirements_critic_height OR
       NEW.arch_requirements_validation_req != OLD.arch_requirements_validation_req OR
       NEW.arch_requirements_acoustic != OLD.arch_requirements_acoustic OR
       NOT (NEW.arch_requirements_int_fenestration <=> OLD.arch_requirements_int_fenestration) OR
       NOT (NEW.arch_requirements_ext_fenestration <=> OLD.arch_requirements_ext_fenestration) OR
       NOT (NEW.arch_requirements_commentary <=> OLD.arch_requirements_commentary) THEN

        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'arch_requirements' AND entity_id = NEW.arch_requirements_id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'arch_requirements',
            NEW.arch_requirements_id,
            'UPDATE',
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(OLD.room_id),
                'critic_length', OLD.arch_requirements_critic_length,
                'critic_width', OLD.arch_requirements_critic_width,
                'critic_height', OLD.arch_requirements_critic_height,
                'validation_req', OLD.arch_requirements_validation_req,
                'acoustic', OLD.arch_requirements_acoustic,
                'int_fenestration', OLD.arch_requirements_int_fenestration,
                'ext_fenestration', OLD.arch_requirements_ext_fenestration,
                'commentary', OLD.arch_requirements_commentary
            ),
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(NEW.room_id),
                'critic_length', NEW.arch_requirements_critic_length,
                'critic_width', NEW.arch_requirements_critic_width,
                'critic_height', NEW.arch_requirements_critic_height,
                'validation_req', NEW.arch_requirements_validation_req,
                'acoustic', NEW.arch_requirements_acoustic,
                'int_fenestration', NEW.arch_requirements_int_fenestration,
                'ext_fenestration', NEW.arch_requirements_ext_fenestration,
                'commentary', NEW.arch_requirements_commentary
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for arch_requirements
CREATE TRIGGER IF NOT EXISTS arch_requirements_after_delete
AFTER DELETE ON arch_requirements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'arch_requirements' AND entity_id = OLD.arch_requirements_id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'arch_requirements',
        OLD.arch_requirements_id,
        'DELETE',
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(OLD.room_id),
            'critic_length', OLD.arch_requirements_critic_length,
            'critic_width', OLD.arch_requirements_critic_width,
            'critic_height', OLD.arch_requirements_critic_height,
            'validation_req', OLD.arch_requirements_validation_req,
            'acoustic', OLD.arch_requirements_acoustic,
            'int_fenestration', OLD.arch_requirements_int_fenestration,
            'ext_fenestration', OLD.arch_requirements_ext_fenestration,
            'commentary', OLD.arch_requirements_commentary
        ),
        NULL,
        current_version,
        current_user_id
    );
END //

-- ============================== RISK_ELEMENTS TRIGGERS ==============================
-- INSERT Trigger for risk_elements
CREATE TRIGGER IF NOT EXISTS risk_elements_after_insert
AFTER INSERT ON risk_elements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'risk_elements',
        NEW.risk_elements_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(NEW.room_id),
            'general', NEW.risk_elements_general,
            'biological', NEW.risk_elements_biological,
            'gas', NEW.risk_elements_gas,
            'liquids', NEW.risk_elements_liquids,
            'other', NEW.risk_elements_other,
            'chemical_products', NEW.risk_elements_chemical_products,
            'commentary', NEW.risk_elements_commentary
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for risk_elements
CREATE TRIGGER IF NOT EXISTS risk_elements_after_update
AFTER UPDATE ON risk_elements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Check if any field has changed using the <=> null-safe comparison operator
    IF NOT (NEW.risk_elements_general <=> OLD.risk_elements_general) OR
       NOT (NEW.risk_elements_biological <=> OLD.risk_elements_biological) OR
       NOT (NEW.risk_elements_gas <=> OLD.risk_elements_gas) OR
       NOT (NEW.risk_elements_liquids <=> OLD.risk_elements_liquids) OR
       NOT (NEW.risk_elements_other <=> OLD.risk_elements_other) OR
       NOT (NEW.risk_elements_chemical_products <=> OLD.risk_elements_chemical_products) OR
       NOT (NEW.risk_elements_commentary <=> OLD.risk_elements_commentary) THEN

        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'risk_elements' AND entity_id = NEW.risk_elements_id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'risk_elements',
            NEW.risk_elements_id,
            'UPDATE',
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(OLD.room_id),
                'general', OLD.risk_elements_general,
                'biological', OLD.risk_elements_biological,
                'gas', OLD.risk_elements_gas,
                'liquids', OLD.risk_elements_liquids,
                'other', OLD.risk_elements_other,
                'chemical_products', OLD.risk_elements_chemical_products,
                'commentary', OLD.risk_elements_commentary
            ),
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(NEW.room_id),
                'general', NEW.risk_elements_general,
                'biological', NEW.risk_elements_biological,
                'gas', NEW.risk_elements_gas,
                'liquids', NEW.risk_elements_liquids,
                'other', NEW.risk_elements_other,
                'chemical_products', NEW.risk_elements_chemical_products,
                'commentary', NEW.risk_elements_commentary
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for risk_elements
CREATE TRIGGER IF NOT EXISTS risk_elements_after_delete
AFTER DELETE ON risk_elements
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'risk_elements' AND entity_id = OLD.risk_elements_id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'risk_elements',
        OLD.risk_elements_id,
        'DELETE',
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(OLD.room_id),
            'general', OLD.risk_elements_general,
            'biological', OLD.risk_elements_biological,
            'gas', OLD.risk_elements_gas,
            'liquids', OLD.risk_elements_liquids,
            'other', OLD.risk_elements_other,
            'chemical_products', OLD.risk_elements_chemical_products,
            'commentary', OLD.risk_elements_commentary
        ),
        NULL,
        current_version,
        current_user_id
    );
END //

-- ============================== VENTILATION_CVAC TRIGGERS ==============================
-- INSERT Trigger for ventilation_cvac
CREATE TRIGGER IF NOT EXISTS ventilation_cvac_after_insert
AFTER INSERT ON ventilation_cvac
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'ventilation_cvac',
        NEW.ventilation_cvac_id,
        'INSERT',
        NULL,
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(NEW.room_id),
            'care_area_type', NEW.ventilation_care_area_type,
            'ventilation', NEW.ventilation,
            'special_mechanics', NEW.ventilation_special_mechanics,
            'specific_exhaust', NEW.ventilation_specific_exhaust,
            'relative_room_pressure', NEW.ventilation_relative_room_pressure,
            'pressurization', NEW.ventilation_pressurization,
            'environmental_parameters', NEW.ventilation_environmental_parameters,
            'commentary', NEW.ventilation_commentary
        ),
        '1.0',
        current_user_id
    );
END //

-- UPDATE Trigger for ventilation_cvac
CREATE TRIGGER IF NOT EXISTS ventilation_cvac_after_update
AFTER UPDATE ON ventilation_cvac
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Check if any field has changed
    IF NOT (NEW.ventilation_care_area_type <=> OLD.ventilation_care_area_type) OR
       NOT (NEW.ventilation <=> OLD.ventilation) OR
       NOT (NEW.ventilation_special_mechanics <=> OLD.ventilation_special_mechanics) OR
       NOT (NEW.ventilation_specific_exhaust <=> OLD.ventilation_specific_exhaust) OR
       NOT (NEW.ventilation_relative_room_pressure <=> OLD.ventilation_relative_room_pressure) OR
       NOT (NEW.ventilation_pressurization <=> OLD.ventilation_pressurization) OR
       NOT (NEW.ventilation_environmental_parameters <=> OLD.ventilation_environmental_parameters) OR
       NOT (NEW.ventilation_commentary <=> OLD.ventilation_commentary) THEN

        -- Get latest version and increment
        SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
        FROM historical_changes
        WHERE entity_type = 'ventilation_cvac' AND entity_id = NEW.ventilation_cvac_id;

        SET current_version = current_version + 0.1;

        -- Insert into historical_changes
        INSERT INTO historical_changes (
            entity_type,
            entity_id,
            change_type,
            old_value,
            new_value,
            version_number,
            user_id
        ) VALUES (
            'ventilation_cvac',
            NEW.ventilation_cvac_id,
            'UPDATE',
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(OLD.room_id),
                'care_area_type', OLD.ventilation_care_area_type,
                'ventilation', OLD.ventilation,
                'special_mechanics', OLD.ventilation_special_mechanics,
                'specific_exhaust', OLD.ventilation_specific_exhaust,
                'relative_room_pressure', OLD.ventilation_relative_room_pressure,
                'pressurization', OLD.ventilation_pressurization,
                'environmental_parameters', OLD.ventilation_environmental_parameters,
                'commentary', OLD.ventilation_commentary
            ),
            JSON_OBJECT(
                'room_id', BIN_TO_UUID(NEW.room_id),
                'care_area_type', NEW.ventilation_care_area_type,
                'ventilation', NEW.ventilation,
                'special_mechanics', NEW.ventilation_special_mechanics,
                'specific_exhaust', NEW.ventilation_specific_exhaust,
                'relative_room_pressure', NEW.ventilation_relative_room_pressure,
                'pressurization', NEW.ventilation_pressurization,
                'environmental_parameters', NEW.ventilation_environmental_parameters,
                'commentary', NEW.ventilation_commentary
            ),
            current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for ventilation_cvac
CREATE TRIGGER IF NOT EXISTS ventilation_cvac_after_delete
AFTER DELETE ON ventilation_cvac
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE current_version DECIMAL(10,1);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SELECT COALESCE(MAX(CAST(version_number AS DECIMAL(10,1))), 0) INTO current_version
    FROM historical_changes
    WHERE entity_type = 'ventilation_cvac' AND entity_id = OLD.ventilation_cvac_id;

    SET current_version = current_version + 0.1;

    -- Insert into historical_changes
    INSERT INTO historical_changes (
        entity_type,
        entity_id,
        change_type,
        old_value,
        new_value,
        version_number,
        user_id
    ) VALUES (
        'ventilation_cvac',
        OLD.ventilation_cvac_id,
        'DELETE',
        JSON_OBJECT(
            'room_id', BIN_TO_UUID(OLD.room_id),
            'care_area_type', OLD.ventilation_care_area_type,
            'ventilation', OLD.ventilation,
            'special_mechanics', OLD.ventilation_special_mechanics,
            'specific_exhaust', OLD.ventilation_specific_exhaust,
            'relative_room_pressure', OLD.ventilation_relative_room_pressure,
            'pressurization', OLD.ventilation_pressurization,
            'environmental_parameters', OLD.ventilation_environmental_parameters,
            'commentary', OLD.ventilation_commentary