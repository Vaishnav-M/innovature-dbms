"""
Product Views

API endpoints for product CRUD operations.
"""

from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Product, ProductImage
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductImageSerializer,
    ProductImageUploadSerializer,
)
from apps.core.permissions import CanManageProducts


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product CRUD operations.
    
    Endpoints:
    - GET    /api/products/           - List all products
    - POST   /api/products/           - Create new product
    - GET    /api/products/{id}/      - Get product details
    - PUT    /api/products/{id}/      - Update product
    - PATCH  /api/products/{id}/      - Partial update product
    - DELETE /api/products/{id}/      - Delete product
    - POST   /api/products/{id}/images/  - Upload images
    - GET    /api/products/{id}/images/  - List product images
    """
    
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, CanManageProducts]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        """
        Get products for the current tenant.
        The database router handles routing to the correct DB.
        """
        queryset = Product.objects.all()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by featured
        is_featured = self.request.query_params.get('featured')
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List products with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Get product details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Product created successfully',
            'data': ProductDetailSerializer(product, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a product."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Product updated successfully',
            'data': ProductDetailSerializer(product, context={'request': request}).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete a product."""
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get', 'post'], url_path='images')
    def images(self, request, id=None):
        """
        GET: List all images for a product.
        POST: Upload new images for a product.
        """
        product = self.get_object()
        
        if request.method == 'GET':
            images = product.images.all()
            serializer = ProductImageSerializer(
                images,
                many=True,
                context={'request': request}
            )
            return Response({
                'success': True,
                'data': serializer.data
            })
        
        elif request.method == 'POST':
            serializer = ProductImageUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            images_data = serializer.validated_data['images']
            set_primary = serializer.validated_data.get('set_primary')
            
            created_images = []
            existing_count = product.images.count()
            
            for index, image_file in enumerate(images_data):
                is_primary = False
                if set_primary is not None and index == set_primary:
                    is_primary = True
                
                product_image = ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    is_primary=is_primary,
                    sort_order=existing_count + index
                )
                created_images.append(product_image)
            
            return Response({
                'success': True,
                'message': f'{len(created_images)} image(s) uploaded successfully',
                'data': ProductImageSerializer(
                    created_images,
                    many=True,
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)


class ProductImageView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual product images.
    
    Endpoints:
    - GET    /api/products/images/{id}/  - Get image details
    - PUT    /api/products/images/{id}/  - Update image (alt_text, is_primary, etc.)
    - DELETE /api/products/images/{id}/  - Delete image
    """
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated, CanManageProducts]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Image updated successfully',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'success': True,
            'message': 'Image deleted successfully'
        }, status=status.HTTP_200_OK)
