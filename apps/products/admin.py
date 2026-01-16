from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['id', 'created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'quantity', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    ordering = ['-created_at']
    inlines = [ProductImageInline]
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
        ('Pricing', {'fields': ('price', 'cost_price')}),
        ('Inventory', {'fields': ('sku', 'quantity')}),
        ('Status', {'fields': ('status', 'is_featured')}),
        ('SEO', {'fields': ('meta_title', 'meta_description')}),
        ('Audit', {'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['id', 'created_at']
    ordering = ['product', 'sort_order']
