"""
Product URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductImageView

app_name = 'products'

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    # Product image management (individual image endpoints)
    path('images/<uuid:id>/', ProductImageView.as_view(), name='product-image-detail'),
    
    # Product CRUD (via router)
    path('', include(router.urls)),
]
