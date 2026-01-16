"""
Authentication Serializers

Serializers for user registration, login, and token management.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify

from .models import Company

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'email', 'phone', 'address', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new company."""
    
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'address']
    
    def validate_name(self, value):
        """Validate and generate slug from name."""
        slug = slugify(value)
        if Company.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(
                "A company with a similar name already exists."
            )
        return value
    
    def create(self, validated_data):
        """Create company with auto-generated slug and db_name."""
        slug = slugify(validated_data['name'])
        validated_data['slug'] = slug
        validated_data['db_name'] = f"tenant_{slug}"
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    company = CompanySerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'company', 'role', 'is_active', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'is_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    company_name = serializers.CharField(write_only=True, required=False)
    company_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'company_name', 'company_id'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation and company."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        # Must provide either company_name (new company) or company_id (existing)
        company_name = attrs.get('company_name')
        company_id = attrs.get('company_id')
        
        if not company_name and not company_id:
            raise serializers.ValidationError({
                'company': "Either company_name or company_id must be provided."
            })
        
        if company_id:
            try:
                attrs['company'] = Company.objects.get(id=company_id, is_active=True)
            except Company.DoesNotExist:
                raise serializers.ValidationError({
                    'company_id': "Company not found or inactive."
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create user and optionally create a new company."""
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        company_name = validated_data.pop('company_name', None)
        validated_data.pop('company_id', None)
        company = validated_data.pop('company', None)
        
        # Create new company if company_name provided
        if company_name and not company:
            slug = slugify(company_name)
            company = Company.objects.create(
                name=company_name,
                slug=slug,
                email=validated_data['email'],  # Use user's email for company
                db_name=f"tenant_{slug}"
            )
            # First user of a new company becomes admin
            validated_data['role'] = 'admin'
        
        validated_data['company'] = company
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that includes company information in the token.
    """
    
    @classmethod
    def get_token(cls, user):
        """Add custom claims to the token."""
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.role
        
        # Add company information (critical for multi-tenancy)
        if user.company:
            token['company_id'] = str(user.company.id)
            token['company_slug'] = user.company.slug
            token['company_name'] = user.company.name
        
        return token
    
    def validate(self, attrs):
        """Validate and add user data to response."""
        data = super().validate(attrs)
        
        # Add user info to response
        data['user'] = UserSerializer(self.user).data
        
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords do not match."
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
