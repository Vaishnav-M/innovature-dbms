"""
Authentication URL Configuration
"""

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshAPIView,
    UserProfileView,
    PasswordChangeView,
    CompanyListView,
)

app_name = 'authentication'

urlpatterns = [
    # Registration and Login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Token management
    path('token/refresh/', TokenRefreshAPIView.as_view(), name='token_refresh'),
    
    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # Company listing (for registration)
    path('companies/', CompanyListView.as_view(), name='company_list'),
]
