"""
Multi-tenant Middleware

This middleware:
1. Validates JWT tokens on protected endpoints
2. Extracts company information from the token
3. Sets the appropriate tenant database context
"""

import logging
from django.http import JsonResponse
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .db_router import set_current_db_name, clear_current_db_name, get_tenant_db_alias

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Middleware to handle multi-tenant database routing.
    
    Flow:
    1. Check if the request is to a protected endpoint
    2. If protected, validate the JWT token
    3. Extract company_slug from the token payload
    4. Set the tenant database context for the request
    5. Clear the context after the request is processed
    """
    
    # Endpoints that don't require authentication
    PUBLIC_PATHS = [
        '/api/auth/login/',
        '/api/auth/register/',
        '/api/auth/token/refresh/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
    
    def __call__(self, request):
        # Clear any existing tenant context
        clear_current_db_name()
        
        # Check if this is a public path
        if self._is_public_path(request.path):
            return self.get_response(request)
        
        # Try to authenticate and set tenant context
        try:
            tenant_db = self._get_tenant_from_request(request)
            if tenant_db:
                set_current_db_name(tenant_db)
                logger.debug(f"Set tenant database context: {tenant_db}")
        except InvalidToken as e:
            logger.warning(f"Invalid token: {e}")
            return JsonResponse(
                {'error': 'Invalid or expired token', 'detail': str(e)},
                status=401
            )
        except TokenError as e:
            logger.warning(f"Token error: {e}")
            return JsonResponse(
                {'error': 'Token error', 'detail': str(e)},
                status=401
            )
        except Exception as e:
            logger.error(f"Unexpected error in tenant middleware: {e}")
            # Don't block the request, let DRF handle auth
            pass
        
        try:
            response = self.get_response(request)
        finally:
            # Always clear the tenant context after the request
            clear_current_db_name()
        
        return response
    
    def _is_public_path(self, path):
        """Check if the path is public (doesn't require authentication)."""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
    
    def _get_tenant_from_request(self, request):
        """
        Extract tenant information from the JWT token.
        Returns the database alias for the tenant.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        # Validate and decode the token
        validated_token = self.jwt_auth.get_validated_token(
            auth_header.split(' ')[1]
        )
        
        # Extract company_slug from token payload
        company_slug = validated_token.get('company_slug')
        
        if not company_slug:
            logger.warning("Token missing company_slug claim")
            return None
        
        # Get or create the tenant database configuration
        return get_tenant_db_alias(company_slug)


class RequestLoggingMiddleware:
    """
    Optional middleware for logging API requests.
    Useful for debugging and monitoring.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log the request
        logger.info(f"{request.method} {request.path}")
        
        response = self.get_response(request)
        
        # Log the response status
        logger.info(f"{request.method} {request.path} -> {response.status_code}")
        
        return response
