#!/usr/bin/env python
"""
Tenant Database Creation Script

This script creates a new tenant database for a company.
It runs migrations to set up the products schema.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')


def create_tenant_database(company_slug: str, run_migrations: bool = True) -> str:
    """
    Create a new tenant database for a company.
    
    Args:
        company_slug: The company's slug (used for database naming)
        run_migrations: Whether to run migrations on the new database
    
    Returns:
        Path to the created database file
    """
    # Get tenant database directory from settings
    tenant_db_dir = BASE_DIR / os.getenv('TENANT_DB_DIR', 'tenant_databases')
    tenant_db_dir.mkdir(exist_ok=True)
    
    # Database file path
    db_path = tenant_db_dir / f"{company_slug}_db.sqlite3"
    
    if db_path.exists():
        print(f"Database already exists: {db_path}")
        return str(db_path)
    
    print(f"Creating tenant database: {db_path}")
    
    # Create the database by connecting to it
    conn = sqlite3.connect(db_path)
    
    if run_migrations:
        # Read and execute the tenant migration script
        migration_file = BASE_DIR / 'migrations' / 'tenant_db_migration.sql'
        
        if migration_file.exists():
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Execute the migration
            conn.executescript(migration_sql)
            print(f"Migrations applied successfully")
        else:
            print(f"Warning: Migration file not found: {migration_file}")
            # Create tables manually as fallback
            _create_tenant_tables(conn)
    
    conn.close()
    print(f"Tenant database created: {db_path}")
    
    return str(db_path)


def _create_tenant_tables(conn: sqlite3.Connection):
    """Create tenant tables manually (fallback if migration file not found)."""
    
    cursor = conn.cursor()
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(280) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) DEFAULT 0.00 NOT NULL,
            cost_price DECIMAL(10, 2),
            sku VARCHAR(100),
            quantity INTEGER DEFAULT 0 NOT NULL,
            status VARCHAR(20) DEFAULT 'draft' NOT NULL,
            is_featured BOOLEAN DEFAULT FALSE NOT NULL,
            meta_title VARCHAR(255),
            meta_description TEXT,
            created_by TEXT,
            updated_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    ''')
    
    # Product Images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_images (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            image VARCHAR(255) NOT NULL,
            alt_text VARCHAR(255),
            is_primary BOOLEAN DEFAULT FALSE NOT NULL,
            sort_order INTEGER DEFAULT 0 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_status ON products(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id)')
    
    conn.commit()
    print("Tenant tables created successfully")


def delete_tenant_database(company_slug: str) -> bool:
    """
    Delete a tenant database.
    
    Args:
        company_slug: The company's slug
    
    Returns:
        True if deleted, False if not found
    """
    tenant_db_dir = BASE_DIR / os.getenv('TENANT_DB_DIR', 'tenant_databases')
    db_path = tenant_db_dir / f"{company_slug}_db.sqlite3"
    
    if db_path.exists():
        os.remove(db_path)
        print(f"Deleted tenant database: {db_path}")
        return True
    else:
        print(f"Database not found: {db_path}")
        return False


def list_tenant_databases() -> list:
    """List all tenant databases."""
    tenant_db_dir = BASE_DIR / os.getenv('TENANT_DB_DIR', 'tenant_databases')
    
    if not tenant_db_dir.exists():
        return []
    
    databases = []
    for db_file in tenant_db_dir.glob("*_db.sqlite3"):
        databases.append({
            'slug': db_file.stem.replace('_db', ''),
            'path': str(db_file),
            'size': db_file.stat().st_size
        })
    
    return databases


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage tenant databases')
    parser.add_argument('action', choices=['create', 'delete', 'list'],
                       help='Action to perform')
    parser.add_argument('--slug', '-s', help='Company slug')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        if not args.slug:
            print("Error: --slug is required for create action")
            sys.exit(1)
        create_tenant_database(args.slug)
    
    elif args.action == 'delete':
        if not args.slug:
            print("Error: --slug is required for delete action")
            sys.exit(1)
        delete_tenant_database(args.slug)
    
    elif args.action == 'list':
        databases = list_tenant_databases()
        if databases:
            print("\nTenant Databases:")
            print("-" * 60)
            for db in databases:
                print(f"  Slug: {db['slug']}")
                print(f"  Path: {db['path']}")
                print(f"  Size: {db['size'] / 1024:.2f} KB")
                print("-" * 60)
        else:
            print("No tenant databases found")
