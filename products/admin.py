from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Review, Wishlist


class CategoryAdmin(admin.ModelAdmin):
    """
    Category Admin - Only Admins can manage categories
    """
    list_display = ('name', 'icon', 'slug', 'product_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def has_add_permission(self, request):
        """Only admins can add categories"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only admins can change categories"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete categories"""
        return request.user.is_superuser


class ProductAdmin(admin.ModelAdmin):
    """
    Product Admin with Role-Based Restrictions
    - Admins: Full CRUD
    - Supervisors: Create, Read, Update (No Delete)
    - Customers: No access
    """
    list_display = ('name', 'category', 'seller', 'price', 'stock', 
                    'eco_score_badge', 'is_active', 'is_featured', 'views_count', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'recyclable', 
                   'biodegradable', 'created_at')
    search_fields = ('name', 'description', 'eco_certifications', 'seller__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_editable = ('is_active', 'is_featured')
    list_per_page = 20
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'category', 'seller', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'compare_price', 'stock')
        }),
        ('Eco Information', {
            'fields': ('eco_score', 'eco_certifications', 'carbon_footprint', 
                       'recyclable', 'biodegradable'),
            'description': 'EcoScore must be between 1-100'
        }),
        ('Images', {
            'fields': ('image', 'image2', 'image3'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def eco_score_badge(self, obj):
        """Display eco score as colored badge"""
        if obj.eco_score >= 90:
            color = '#10b981'  # green
        elif obj.eco_score >= 70:
            color = '#f59e0b'  # yellow
        else:
            color = '#ef4444'  # red
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.eco_score
        )
    eco_score_badge.short_description = 'EcoScore'
    eco_score_badge.admin_order_field = 'eco_score'
    
    def has_add_permission(self, request):
        """Admins and Supervisors can add products"""
        return request.user.is_superuser or request.user.role == 'supervisor'
    
    def has_change_permission(self, request, obj=None):
        """Admins and Supervisors can change products"""
        return request.user.is_superuser or request.user.role == 'supervisor'
    
    def has_delete_permission(self, request, obj=None):
        """Only Admins can delete products"""
        return request.user.is_superuser
    
    def get_actions(self, request):
        """Remove delete action for supervisors"""
        actions = super().get_actions(request)
        if not request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class ReviewAdmin(admin.ModelAdmin):
    """
    Review Admin with Role-Based Restrictions
    - Admins: Full CRUD
    - Supervisors: Read, Moderate (approve/hide) - No Delete
    - Customers: No access
    """
    list_display = ('product', 'user', 'rating_stars', 'title', 
                    'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('product', 'user', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_editable = ('is_approved',)
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        return '⭐' * obj.rating
    rating_stars.short_description = 'Rating'
    
    def has_add_permission(self, request):
        """Reviews are added by customers, not in admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Admins and Supervisors can moderate reviews"""
        return request.user.is_superuser or request.user.role == 'supervisor'
    
    def has_delete_permission(self, request, obj=None):
        """Only Admins can delete reviews"""
        return request.user.is_superuser
    
    def get_readonly_fields(self, request, obj=None):
        """Supervisors can only change is_approved"""
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly.extend(['rating', 'title', 'comment', 'is_verified_purchase'])
        return readonly
    
    def get_actions(self, request):
        """Remove delete action for supervisors"""
        actions = super().get_actions(request)
        if not request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class WishlistAdmin(admin.ModelAdmin):
    """
    Wishlist Admin - Read Only for all
    """
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('user', 'product', 'added_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
