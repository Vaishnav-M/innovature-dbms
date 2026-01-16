#!/usr/bin/env python
"""
Sample Data Seeder Script

This script seeds the database with sample data for testing.
"""

import os
import sys
import uuid
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import Company
from apps.products.models import Product, ProductImage
from apps.core.db_router import set_current_db_name, get_tenant_db_alias
from scripts.create_tenant_db import create_tenant_database

User = get_user_model()


def seed_companies():
    """Create sample companies."""
    companies_data = [
        {
            'name': 'Acme Corporation',
            'slug': 'acme-corporation',
            'email': 'admin@acme.com',
            'phone': '+1-555-0100',
            'address': '123 Business Ave, New York, NY 10001',
        },
        {
            'name': 'Tech Solutions Inc',
            'slug': 'tech-solutions-inc',
            'email': 'admin@techsolutions.com',
            'phone': '+1-555-0200',
            'address': '456 Innovation Blvd, San Francisco, CA 94105',
        },
        {
            'name': 'Global Retail Co',
            'slug': 'global-retail-co',
            'email': 'admin@globalretail.com',
            'phone': '+1-555-0300',
            'address': '789 Commerce St, Chicago, IL 60601',
        },
    ]
    
    created_companies = []
    
    for data in companies_data:
        company, created = Company.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'name': data['name'],
                'email': data['email'],
                'phone': data['phone'],
                'address': data['address'],
                'db_name': f"tenant_{data['slug']}",
            }
        )
        
        if created:
            print(f"Created company: {company.name}")
            # Create tenant database
            create_tenant_database(company.slug)
        else:
            print(f"Company already exists: {company.name}")
        
        created_companies.append(company)
    
    return created_companies


def seed_users(companies):
    """Create sample users for each company."""
    
    for company in companies:
        # Create admin user
        admin_email = f"admin@{company.slug.replace('-', '')}.com"
        admin, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Admin',
                'last_name': company.name.split()[0],
                'company': company,
                'role': 'admin',
                'is_active': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            print(f"Created admin user: {admin.email}")
        
        # Create manager user
        manager_email = f"manager@{company.slug.replace('-', '')}.com"
        manager, created = User.objects.get_or_create(
            email=manager_email,
            defaults={
                'first_name': 'Manager',
                'last_name': company.name.split()[0],
                'company': company,
                'role': 'manager',
                'is_active': True,
            }
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            print(f"Created manager user: {manager.email}")
        
        # Create regular user
        user_email = f"user@{company.slug.replace('-', '')}.com"
        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={
                'first_name': 'User',
                'last_name': company.name.split()[0],
                'company': company,
                'role': 'user',
                'is_active': True,
            }
        )
        if created:
            user.set_password('user123')
            user.save()
            print(f"Created regular user: {user.email}")


def seed_products(companies):
    """Create sample products for each company."""
    
    products_data = [
        {
            'name': 'Wireless Keyboard Pro',
            'description': 'Ergonomic wireless keyboard with backlit keys and long battery life. Features quiet mechanical switches.',
            'price': 79.99,
            'cost_price': 45.00,
            'sku': 'KB-001',
            'quantity': 150,
            'status': 'active',
            'is_featured': True,
        },
        {
            'name': 'USB-C Hub 7-in-1',
            'description': 'Premium USB-C hub with HDMI 4K, SD card reader, USB 3.0 ports, and power delivery.',
            'price': 49.99,
            'cost_price': 25.00,
            'sku': 'HUB-001',
            'quantity': 200,
            'status': 'active',
            'is_featured': False,
        },
        {
            'name': 'Wireless Mouse Silent',
            'description': 'Ultra-quiet wireless mouse with ergonomic design. 3-year battery life, DPI adjustable.',
            'price': 39.99,
            'cost_price': 18.00,
            'sku': 'MS-001',
            'quantity': 300,
            'status': 'active',
            'is_featured': True,
        },
        {
            'name': 'Laptop Stand Aluminum',
            'description': 'Premium aluminum laptop stand with adjustable height. Compatible with all laptops up to 17 inches.',
            'price': 59.99,
            'cost_price': 30.00,
            'sku': 'LS-001',
            'quantity': 100,
            'status': 'active',
            'is_featured': False,
        },
        {
            'name': 'Webcam HD 1080p',
            'description': 'Full HD webcam with auto-focus, built-in microphone, and privacy cover.',
            'price': 69.99,
            'cost_price': 35.00,
            'sku': 'WC-001',
            'quantity': 75,
            'status': 'active',
            'is_featured': True,
        },
        {
            'name': 'Desk Organizer Set',
            'description': 'Modern desk organizer with pen holder, phone stand, and cable management.',
            'price': 29.99,
            'cost_price': 12.00,
            'sku': 'DO-001',
            'quantity': 250,
            'status': 'draft',
            'is_featured': False,
        },
    ]
    
    for company in companies:
        print(f"\nSeeding products for: {company.name}")
        
        # Set the tenant database context
        db_alias = get_tenant_db_alias(company.slug)
        set_current_db_name(db_alias)
        
        for data in products_data:
            # Add company-specific prefix to SKU to make it unique
            sku = f"{company.slug[:3].upper()}-{data['sku']}"
            
            product, created = Product.objects.using(db_alias).get_or_create(
                sku=sku,
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'price': data['price'],
                    'cost_price': data['cost_price'],
                    'quantity': data['quantity'],
                    'status': data['status'],
                    'is_featured': data['is_featured'],
                }
            )
            
            if created:
                print(f"  Created product: {product.name} ({sku})")
            else:
                print(f"  Product already exists: {product.name} ({sku})")


def seed_superuser():
    """Create a superuser for Django admin."""
    
    superuser_email = 'superadmin@productmanagement.local'
    
    if not User.objects.filter(email=superuser_email).exists():
        User.objects.create_superuser(
            email=superuser_email,
            password='superadmin123',
            first_name='Super',
            last_name='Admin',
        )
        print(f"\nCreated superuser: {superuser_email}")
        print("Password: superadmin123")
    else:
        print(f"\nSuperuser already exists: {superuser_email}")


def main():
    """Run all seeders."""
    print("=" * 60)
    print("SEEDING DATABASE WITH SAMPLE DATA")
    print("=" * 60)
    
    print("\n1. Creating companies...")
    companies = seed_companies()
    
    print("\n2. Creating users...")
    seed_users(companies)
    
    print("\n3. Creating products...")
    seed_products(companies)
    
    print("\n4. Creating superuser...")
    seed_superuser()
    
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE!")
    print("=" * 60)
    
    print("\nSample Login Credentials:")
    print("-" * 40)
    print("Company 1 (Acme Corporation):")
    print("  Admin:   admin@acmecorporation.com / admin123")
    print("  Manager: manager@acmecorporation.com / manager123")
    print("  User:    user@acmecorporation.com / user123")
    print("-" * 40)
    print("Company 2 (Tech Solutions Inc):")
    print("  Admin:   admin@techsolutionsinc.com / admin123")
    print("-" * 40)
    print("Superuser (Django Admin):")
    print("  superadmin@productmanagement.local / superadmin123")
    print("-" * 40)


if __name__ == '__main__':
    main()
