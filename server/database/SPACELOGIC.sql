CREATE DATABASE IF NOT EXISTS SPACELOGIC_users;
CREATE DATABASE IF NOT EXISTS SPACELOGIC_projet1;

# Section BD administrative
# ----------------------------TABLES---------------------------
USE SPACELOGIC_users;

CREATE TABLE IF NOT EXISTS organisations (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    super_admin_id BINARY(16),
    PRIMARY KEY (id),
    UNIQUE(nom)
);

CREATE TABLE IF NOT EXISTS users (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    org_id BINARY(16) NOT NULL,
    role VARCHAR(255),
    company VARCHAR(255),
    department VARCHAR(255),
    location VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOL DEFAULT TRUE NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (org_id)
    REFERENCES organisations(id),
    UNIQUE (email)
);

ALTER TABLE organisations
    ADD CONSTRAINT fk_super_admin_id
    FOREIGN KEY (super_admin_id) REFERENCES users(id)
    ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS projects (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    org_id BINARY(16),
    numero VARCHAR(25) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ended_at DATETIME,
    status VARCHAR(25),
    type VARCHAR(25),
    PRIMARY KEY (id),
    UNIQUE (numero),
    FOREIGN KEY (org_id)
    REFERENCES organisations(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

# Section BD projet (une par projet)
# ----------------------------TABLES---------------------------
USE SPACELOGIC_projet1;

CREATE TABLE IF NOT EXISTS rooms (
    no_programme VARCHAR(50),
    nom VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    secteur VARCHAR(50),
    unite_fonctionnelle VARCHAR(50),
    niveau VARCHAR(50),
    superficie_programme DOUBLE NOT NULL,
    PRIMARY KEY (no_programme)
);

# CREATE TABLE IF NOT EXISTS disciplines (
#     nom VARCHAR(50),
#     PRIMARY KEY (nom)
# );

CREATE TABLE IF NOT EXISTS historicalChanges (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BINARY(16) NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    old_value VARCHAR(25),
    new_value VARCHAR(25),
    change_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    version_number VARCHAR(25) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS organisationRoles (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    organisation_id BINARY(16) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (organisation_id)
    REFERENCES SPACELOGIC_users.organisations (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS planAbonnement (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    prix DECIMAL(10,2) NOT NULL,
    features VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    UNIQUE(nom)
);

CREATE TABLE IF NOT EXISTS finition (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    pj VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);

#-----------------------------RELATIONS-----------------------------

CREATE TABLE IF NOT EXISTS organisation_user (
    organisations_id BINARY(16) NOT NULL,
    users_id BINARY(16) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (organisations_id, users_id),
    FOREIGN KEY (organisations_id)
    REFERENCES SPACELOGIC_users.organisations (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (users_id)
    REFERENCES SPACELOGIC_users.users (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS user_organisation_role (
    user_id BINARY(16) NOT NULL,
    organisation_id BINARY(16) NOT NULL,
    role_id BINARY(16) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, organisation_id, role_id),
    FOREIGN KEY (user_id) REFERENCES SPACELOGIC_users.users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (organisation_id) REFERENCES SPACELOGIC_users.organisations(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES organisationRoles(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS project_user (
    project_id BINARY(16) NOT NULL,
    user_id BINARY(16) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id)
    REFERENCES SPACELOGIC_users.projects (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES SPACELOGIC_users.users (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

#À garder si on crée plus d'une database?
CREATE TABLE IF NOT EXISTS room_project (
    project_id BINARY(16) NOT NULL,
    room_no_programme VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (project_id, room_no_programme),
    FOREIGN KEY (project_id)
    REFERENCES SPACELOGIC_users.projects(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (room_no_programme)
    REFERENCES rooms (no_programme)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

# CREATE TABLE IF NOT EXISTS discipline_room (
#     room_no_programme VARCHAR(50) NOT NULL,
#     discipline_nom VARCHAR(50) NOT NULL,
#     PRIMARY KEY (room_no_programme, discipline_nom),
#     FOREIGN KEY (discipline_nom)
#     REFERENCES disciplines(nom)
#     ON DELETE CASCADE
#     ON UPDATE CASCADE,
#     FOREIGN KEY (room_no_programme)
#     REFERENCES rooms (no_programme)
#     ON DELETE CASCADE
#     ON UPDATE CASCADE
# );

#-----------------------------Procédures--------------------------------------

#-----------------------------Procédures--------------------------------------


#-----------------------------Données par défauts-----------------------------

-- Create organisation first without super_admin_id
INSERT INTO SPACELOGIC_users.organisations (nom, super_admin_id)
VALUES ('Gucci Gang', NULL);

-- Get the organisation ID
SET @org_id = (SELECT id FROM SPACELOGIC_users.organisations WHERE nom = 'Gucci Gang');

-- Insert user with organisation ID
INSERT INTO SPACELOGIC_users.users (nom, prenom, email, password, org_id)
VALUES ('Sébastien', 'Gagnon', 'sgagnon@stgm.net', '$2b$12$ZXYdUk9rLwY731UuTtpw0.kF7DXpGj8X/soFJ5yAmO1zHqbyqQiEa', @org_id),
       ('Presley', 'Elvis', 'mort@dead.com', '$2b$12$ZXYdUk9rLwY731UuTtpw0.kF7DXpGj8X/soFJ5yAmO1zHqbyqQiEa', @org_id),
       ('Shady', 'Slim', 'Mynameis@eminem.com', '$2b$12$ZXYdUk9rLwY731UuTtpw0.kF7DXpGj8X/soFJ5yAmO1zHqbyqQiEa', @org_id);

-- Get the user ID
SET @user_id_Seb = (SELECT id FROM SPACELOGIC_users.users WHERE email = 'sgagnon@stgm.net');
SET @user_id_1 = (SELECT id FROM SPACELOGIC_users.users WHERE email = 'mort@dead.com');
SET @user_id_2 = (SELECT id FROM SPACELOGIC_users.users WHERE email = 'Mynameis@eminem.com');

-- Update organisation with super_admin_id
UPDATE SPACELOGIC_users.organisations
SET super_admin_id = @user_id_Seb
WHERE nom = 'Gucci Gang';

-- Insert organisation roles
INSERT INTO SPACELOGIC_projet1.organisationRoles (organisation_id, nom, description)
VALUES (@org_id, 'Administrateur', 'un king pin'),
       (@org_id, 'Collaborateur', 'un doer'),
       (@org_id, 'Client', 'un exigeant');

-- Insert user-organisation relationship
INSERT INTO SPACELOGIC_projet1.organisation_user (organisations_id, users_id)
VALUES (@org_id, @user_id_Seb),
       (@org_id, @user_id_1),
       (@org_id, @user_id_2);

-- Insert project
INSERT INTO SPACELOGIC_users.projects (org_id, numero, nom, description)
VALUES (@org_id, 'GLO-2005', 'DÉMO', 'Ceci est un projet test'),
       (@org_id, 'S-24130','Hôpital de Baie-Saint-Paul','Très bel hôpital');

INSERT INTO SPACELOGIC_projet1.project_user (project_id, user_id)
VALUES ((SELECT id FROM SPACELOGIC_users.projects WHERE numero ='GLO-2005'),@user_id_Seb);