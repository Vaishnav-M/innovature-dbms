"""
Product Serializers

Serializers for product CRUD operations with image handling.
"""

from rest_framework import serializers
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """Get the full URL for the image."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing products (lightweight)."""
    
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'quantity',
            'status', 'is_featured', 'primary_image', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get the primary image URL."""
        image = obj.primary_image
        if image and image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product details (full)."""
    
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'cost_price', 'sku', 'quantity',
            'status', 'is_featured',
            'meta_title', 'meta_description',
            'images', 'created_by', 'updated_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_by', 'updated_by', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products."""
    
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'cost_price',
            'sku', 'quantity', 'status', 'is_featured',
            'meta_title', 'meta_description', 'images'
        ]
    
    def create(self, validated_data):
        """Create product with images."""
        images_data = validated_data.pop('images', [])
        
        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user.id
        
        product = Product.objects.create(**validated_data)
        
        # Create product images
        for index, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_data,
                is_primary=(index == 0),  # First image is primary
                sort_order=index
            )
        
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'cost_price',
            'sku', 'quantity', 'status', 'is_featured',
            'meta_title', 'meta_description'
        ]
    
    def update(self, instance, validated_data):
        """Update product."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user.id
        
        return super().update(instance, validated_data)


class ProductImageUploadSerializer(serializers.Serializer):
    """Serializer for uploading product images."""
    
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        min_length=1
    )
    set_primary = serializers.IntegerField(
        required=False,
        default=None,
        help_text="Index of image to set as primary (0-based)"
    )
    
    def validate_images(self, value):
        """Validate image files."""
        max_size = 5 * 1024 * 1024  # 5MB
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        for image in value:
            if image.size > max_size:
                raise serializers.ValidationError(
                    f"Image {image.name} exceeds maximum size of 5MB"
                )
            if image.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"Image {image.name} has unsupported format. "
                    f"Allowed: JPEG, PNG, GIF, WebP"
                )
        
        return value
