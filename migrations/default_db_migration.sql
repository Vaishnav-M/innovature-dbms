-- Default Database Migration Script
-- This database stores authentication and company metadata
-- Run this script to create the default database schema

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    db_name VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_companies_slug ON companies(slug);
CREATE INDEX IF NOT EXISTS idx_companies_is_active ON companies(is_active);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    company_id TEXT REFERENCES companies(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login DATETIME
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- User permissions (for Django admin)
CREATE TABLE IF NOT EXISTS users_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users_user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL
);

-- Token blacklist (for JWT logout)
CREATE TABLE IF NOT EXISTS token_blacklist_blacklistedtoken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id INTEGER UNIQUE NOT NULL,
    blacklisted_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS token_blacklist_outstandingtoken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    jti VARCHAR(255) UNIQUE NOT NULL,
    token TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_outstanding_token_jti ON token_blacklist_outstandingtoken(jti);
CREATE INDEX IF NOT EXISTS idx_outstanding_token_user_id ON token_blacklist_outstandingtoken(user_id);

-- Sample data for testing
-- Uncomment to insert test data

-- INSERT INTO companies (id, name, slug, email, db_name) VALUES
--     ('11111111-1111-1111-1111-111111111111', 'Acme Corporation', 'acme-corporation', 'admin@acme.com', 'tenant_acme-corporation'),
--     ('22222222-2222-2222-2222-222222222222', 'Tech Solutions Inc', 'tech-solutions-inc', 'admin@techsolutions.com', 'tenant_tech-solutions-inc');
