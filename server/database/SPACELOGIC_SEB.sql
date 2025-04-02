CREATE DATABASE IF NOT EXISTS SPACELOGIC_ADMIN_DB;
USE SPACELOGIC_ADMIN_DB;

# Section BD administrative
# ----------------------------TABLES---------------------------
-- Organizations table
CREATE TABLE organizations (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    super_admin_id BINARY(16),
    UNIQUE(name)
);

-- Users table
CREATE TABLE users (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    organization_id BINARY(16) NOT NULL,
    role VARCHAR(50),
    department VARCHAR(100),
    location VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    UNIQUE(email)
);

-- Add foreign key constraint for super_admin
ALTER TABLE organizations
    ADD CONSTRAINT fk_super_admin
    FOREIGN KEY (super_admin_id) REFERENCES users(id)
    ON UPDATE CASCADE;

-- Organization roles
CREATE TABLE organization_roles (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
    organization_id BINARY(16) NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
    ON DELETE CASCADE
);

-- Projects
CREATE TABLE projects (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
    organization_id BINARY(16) NOT NULL,
    project_number VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_date DATETIME,
    status VARCHAR(50) DEFAULT 'active',
    type VARCHAR(50),
    image_url VARCHAR(255) DEFAULT ('/static/images/project-placeholder.png'),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    UNIQUE(project_number)
);

-- Create invitations table
CREATE TABLE IF NOT EXISTS organization_invitations (
    id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())) PRIMARY KEY,
    organization_id BINARY(16) NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    location VARCHAR(100),
    token VARCHAR(100) NOT NULL,
    invited_by BINARY(16) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    status ENUM('pending', 'accepted', 'expired', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY (email, organization_id, status)
);

CREATE INDEX idx_token ON organization_invitations(token);

#-----------------------------RELATIONS-----------------------------

-- User-organization relationship
CREATE TABLE organization_user (
    organizations_id BINARY(16) NOT NULL,
    users_id BINARY(16) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (organizations_id, users_id),
    FOREIGN KEY (organizations_id)
    REFERENCES organizations(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    FOREIGN KEY (users_id)
    REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- User-organization-role assignment
CREATE TABLE user_organisation_role (
    user_id BINARY(16) NOT NULL,
    organisation_id BINARY(16) NOT NULL,
    role_id BINARY(16) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, organisation_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (organisation_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES organization_roles(id) ON DELETE CASCADE
);

-- Project user assignment
CREATE TABLE project_users (
    project_id BINARY(16) NOT NULL,
    user_id BINARY(16) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

# ----------------------------PROCEDURES---------------------------

DELIMITER //
CREATE PROCEDURE get_user_project_databases(IN p_user_id BINARY(16))
BEGIN
    SELECT p.id, p.name AS project_name, p.project_number,
           CONCAT('SPACELOGIC_', p.project_number) AS db_name
    FROM projects p
    JOIN project_users pu ON p.id = pu.project_id
    WHERE pu.user_id = p_user_id;
END //
DELIMITER ;

# ----------------------------SAMPLE DATA---------------------------

-- Create organisation first without super_admin_id
INSERT INTO organizations (name, super_admin_id)
VALUES ('Gucci Gang', NULL);

-- Get the organisation ID
SET @org_id = (SELECT id FROM organizations WHERE name = 'Gucci Gang');

-- Insert user with organisation ID
INSERT INTO users (first_name, last_name, email, password, organization_id)
VALUES ('Sébastien', 'Gagnon', 'sgagnon@stgm.net', '$2b$12$ZXYdUk9rLwY731UuTtpw0.kF7DXpGj8X/soFJ5yAmO1zHqbyqQiEa', @org_id),
       ('Presley', 'Elvis', 'mort@dead.com', '$2b$12$ZXYdUk9rLwY731UuTtpw0.kF7DXpGj8X/soFJ5yAmO1zHqbyqQiEa', @org_id),
       ('Shady', 'Slim', 'Mynameis@eminem.com', '$2b$12$ZXYdUk9rLwY731UuTtpw0.kF7DXpGj8X/soFJ5yAmO1zHqbyqQiEa', @org_id);

-- Get the user ID
SET @user_id_Seb = (SELECT id FROM users WHERE email = 'sgagnon@stgm.net');
SET @user_id_1 = (SELECT id FROM users WHERE email = 'mort@dead.com');
SET @user_id_2 = (SELECT id FROM users WHERE email = 'Mynameis@eminem.com');

-- Update organisation with super_admin_id
UPDATE organizations
SET super_admin_id = @user_id_Seb
WHERE name = 'Gucci Gang';

-- Insert organisation roles
INSERT INTO organization_roles (organization_id, name, description)
VALUES (@org_id, 'Administrateur', 'un king pin'),
       (@org_id, 'Collaborateur', 'un doer'),
       (@org_id, 'Client', 'un exigeant');

-- Insert user-organisation relationship
INSERT INTO organization_user (organizations_id, users_id)
VALUES (@org_id, @user_id_Seb),
       (@org_id, @user_id_1),
       (@org_id, @user_id_2);

