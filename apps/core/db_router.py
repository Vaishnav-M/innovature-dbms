"""
Multi-tenant Database Router

This router directs database operations to the appropriate database:
- Default database: User, Company, Token (shared across all tenants)
- Tenant databases: Product, ProductImage (isolated per company)
"""

import threading
from django.conf import settings

# Thread-local storage for current tenant database
_thread_locals = threading.local()


def get_current_db_name():
    """Get the current tenant database name from thread-local storage."""
    return getattr(_thread_locals, 'db_name', None)


def set_current_db_name(db_name):
    """Set the current tenant database name in thread-local storage."""
    _thread_locals.db_name = db_name


def clear_current_db_name():
    """Clear the current tenant database name from thread-local storage."""
    if hasattr(_thread_locals, 'db_name'):
        del _thread_locals.db_name


def get_tenant_db_alias(company_slug):
    """
    Get or create database configuration for a tenant.
    Returns the database alias for the company.
    """
    db_alias = f'tenant_{company_slug}'
    
    if db_alias not in settings.DATABASES:
        # Dynamically add tenant database configuration
        db_path = settings.TENANT_DB_DIR / f'{company_slug}_db.sqlite3'
        settings.DATABASES[db_alias] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
            'ATOMIC_REQUESTS': False,
            'AUTOCOMMIT': True,
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': False,
            'OPTIONS': {},
            'TIME_ZONE': None,
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'TEST': {
                'CHARSET': None,
                'COLLATION': None,
                'MIGRATE': True,
                'MIRROR': None,
                'NAME': None,
            },
        }
    
    return db_alias


class TenantDatabaseRouter:
    """
    A database router to control database operations for multi-tenancy.
    
    Routes:
    - authentication app models → default database
    - core app models → default database  
    - products app models → tenant database (based on current context)
    """
    
    # Models that should always use the default database
    DEFAULT_DB_APPS = {'authentication', 'auth', 'contenttypes', 'sessions', 'admin'}
    
    # Models that should use tenant databases
    TENANT_DB_APPS = {'products'}
    
    def db_for_read(self, model, **hints):
        """
        Route read operations to the appropriate database.
        """
        app_label = model._meta.app_label
        
        if app_label in self.DEFAULT_DB_APPS:
            return 'default'
        
        if app_label in self.TENANT_DB_APPS:
            db_name = get_current_db_name()
            if db_name:
                return db_name
            # Fallback to default if no tenant context
            return 'default'
        
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Route write operations to the appropriate database.
        """
        app_label = model._meta.app_label
        
        if app_label in self.DEFAULT_DB_APPS:
            return 'default'
        
        if app_label in self.TENANT_DB_APPS:
            db_name = get_current_db_name()
            if db_name:
                return db_name
            # Fallback to default if no tenant context
            return 'default'
        
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database category.
        """
        app1 = obj1._meta.app_label
        app2 = obj2._meta.app_label
        
        # Both in default apps
        if app1 in self.DEFAULT_DB_APPS and app2 in self.DEFAULT_DB_APPS:
            return True
        
        # Both in tenant apps
        if app1 in self.TENANT_DB_APPS and app2 in self.TENANT_DB_APPS:
            return True
        
        # Disallow cross-database relations
        return False
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control which models get migrated to which database.
        """
        if app_label in self.DEFAULT_DB_APPS:
            return db == 'default'
        
        if app_label in self.TENANT_DB_APPS:
            # Allow migration to any non-default database (tenant dbs)
            # or to default during initial setup
            return db != 'default' or db == 'default'
        
        return db == 'default'
