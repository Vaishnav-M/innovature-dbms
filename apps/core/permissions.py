"""
Custom Permission Classes for Multi-Tenant Authorization
"""

from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)


class IsCompanyMember(permissions.BasePermission):
    """
    Permission class to ensure user belongs to the company they're accessing.
    """
    message = "You do not have permission to access this company's resources."
    
    def has_permission(self, request, view):
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has a company
        if not hasattr(request.user, 'company') or not request.user.company:
            logger.warning(f"User {request.user.id} has no associated company")
            return False
        
        return True


class IsCompanyAdmin(permissions.BasePermission):
    """
    Permission class to ensure user is an admin of their company.
    """
    message = "You must be a company admin to perform this action."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'company') or not request.user.company:
            return False
        
        return request.user.role == 'admin'


class IsCompanyAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to all authenticated users,
    but write access only to company admins.
    """
    message = "You must be a company admin to modify resources."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'company') or not request.user.company:
            return False
        
        # Allow read-only access for all authenticated company members
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access only for admins
        return request.user.role == 'admin'


class CanManageProducts(permissions.BasePermission):
    """
    Permission class for product management.
    Admins and managers can create/update/delete products.
    Regular users can only view.
    """
    message = "You do not have permission to manage products."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'company') or not request.user.company:
            return False
        
        # Allow read-only access for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access for admins and managers
        return request.user.role in ['admin', 'manager']
