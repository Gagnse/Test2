CREATE DATABASE IF NOT EXISTS SPACELOGIC;
USE SPACELOGIC;

# Section administrative
# ----------------------------TABLES---------------------------
CREATE TABLE IF NOT EXISTS users (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    company VARCHAR(255),
    department VARCHAR(255),
    location VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOL DEFAULT TRUE NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS organisations (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    super_admin_id BINARY(16) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (super_admin_id)
    REFERENCES users(id)
    ON UPDATE CASCADE,
    UNIQUE(nom)
);

CREATE TABLE IF NOT EXISTS projects (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) NOT NULL,
    numero VARCHAR(25) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ended_at DATETIME,
    status VARCHAR(25),
    type VARCHAR(25),
    PRIMARY KEY (id),
    UNIQUE (numero)
);

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

CREATE TABLE IF NOT EXISTS disciplines (
    nom VARCHAR(50),
    PRIMARY KEY (nom)
);

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
    REFERENCES organisations (id)
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
    REFERENCES organisations (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (users_id)
    REFERENCES users (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS user_organisation_role (
    user_id BINARY(16) NOT NULL,
    organisation_id BINARY(16) NOT NULL,
    role_id BINARY(16) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, organisation_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (organisation_id) REFERENCES organisations(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES organisationRoles(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS project_user (
    project_id BINARY(16) NOT NULL,
    user_id BINARY(16) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id)
    REFERENCES projects (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (user_id)
    REFERENCES users (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
 
CREATE TABLE IF NOT EXISTS room_project (
    project_id BINARY(16) NOT NULL,
    room_no_programme VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (project_id, room_no_programme),
    FOREIGN KEY (project_id)
    REFERENCES projects(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (room_no_programme)
    REFERENCES rooms (no_programme)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS discipline_room (
    room_no_programme VARCHAR(50) NOT NULL,
    discipline_nom VARCHAR(50) NOT NULL,
    PRIMARY KEY (room_no_programme, discipline_nom),
    FOREIGN KEY (discipline_nom)
    REFERENCES disciplines(nom)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (room_no_programme)
    REFERENCES rooms (no_programme)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

#-----------------------------Procédures--------------------------------------


#-----------------------------Données par défauts-----------------------------

INSERT INTO users (id,nom, prenom, email, password)
     VALUES (UUID_TO_BIN('a866a2db-facb-11ef-ac88-ac1a3d8285ba'),"Sébastien","Gagnon","sgagnon@stgm.net","$2b$12$E/yJZ6vH2A6Msr/lHkvkJ.yJsMVyvc6H2c7pi7kGzq8jsCz0Ni.O.")
;

INSERT INTO organisationRoles (organisation_id, nom, description)
    VALUES ((SELECT id FROM organisations WHERE nom = 'Gucci Gang'),'Administrateur','un king pin'),
           ((SELECT id FROM organisations WHERE nom = 'Gucci Gang'),'Collaborateur','un doer'),
           ((SELECT id FROM organisations WHERE nom = 'Gucci Gang'),'Client','un exigeant')
;

INSERT INTO organisations (nom, super_admin_id)
    VALUES ('Gucci Gang',(SELECT id FROM users WHERE email= 'sgagnon@stgm.net'))
;

INSERT INTO projects (numero, nom, description)
    VALUES ("GLO-2005","DÉMO","Ceci est un projet test")
;