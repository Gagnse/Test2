DELIMITER //

-- INSERT Trigger for rooms
CREATE TRIGGER rooms_after_insert
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
CREATE TRIGGER rooms_after_update
AFTER UPDATE ON rooms
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);
    DECLARE changes JSON;

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
        SET @current_version = (
            SELECT MAX(CAST(version_number AS DECIMAL(10,1)))
            FROM historical_changes
            WHERE entity_type = 'room' AND entity_id = NEW.id
        );

        IF @current_version IS NULL THEN
            SET @current_version = 1.0;
        ELSE
            SET @current_version = @current_version + 0.1;
        END IF;

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
            @current_version,
            current_user_id
        );
    END IF;
END //

-- DELETE Trigger for rooms
CREATE TRIGGER rooms_after_delete
AFTER DELETE ON rooms
FOR EACH ROW
BEGIN
    DECLARE current_user_id BINARY(16);

    -- Get current user_id from session variable if available
    SET current_user_id = @current_user_id;

    -- Get latest version and increment
    SET @current_version = (
        SELECT MAX(CAST(version_number AS DECIMAL(10,1)))
        FROM historical_changes
        WHERE entity_type = 'room' AND entity_id = OLD.id
    );

    IF @current_version IS NULL THEN
        SET @current_version = 1.0;
    ELSE
        SET @current_version = @current_version + 0.1;
    END IF;

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
        @current_version,
        current_user_id
    );
END //

DELIMITER ;