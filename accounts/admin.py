from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserActivity
from core.emails import send_order_shipped_email, send_order_delivered_email



class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with Role-Based Access Control
    """
    list_display = ('username', 'email', 'role_badge', 'first_name', 'last_name', 
                    'eco_points', 'total_orders', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'is_seller', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    # Fields shown when editing a user
    fieldsets = (
        ('Login Info', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_picture')
        }),
        ('Address', {
            'fields': ('address', 'city', 'country', 'postal_code'),
            'classes': ('collapse',)
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_seller'),
            'description': 'Role determines access level. Admin has full access, Supervisor has limited access, Customer can only shop.'
        }),
        ('Eco Metrics', {
            'fields': ('eco_points', 'total_orders', 'co2_saved'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields shown when creating a new user
    add_fieldsets = (
        ('Login Info', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone'),
        }),
        ('Role', {
            'classes': ('wide',),
            'fields': ('role',),
        }),
    )
    
    def role_badge(self, obj):
        """Display role as colored badge"""
        colors = {
            'admin': 'red',
            'supervisor': 'blue',
            'customer': 'green'
        }
        color = colors.get(obj.role, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
    
    def get_queryset(self, request):
        """
        Supervisors can only view customers, not other supervisors or admins
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'supervisor':
            # Supervisors can see customers and themselves
            return qs.filter(role='customer') | qs.filter(pk=request.user.pk)
        return qs.filter(pk=request.user.pk)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Supervisors cannot change roles
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly.extend(['role', 'is_staff', 'is_superuser', 'is_active'])
        return readonly
    
    def has_add_permission(self, request):
        """Only admins can add users"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete users"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Supervisors can only view, not change users (except themselves)"""
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        # Users can only edit themselves
        return obj == request.user


class UserActivityAdmin(admin.ModelAdmin):
    """
    Admin for User Activity tracking
    """
    list_display = ('user', 'page_visited', 'timestamp', 'ip_address')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'page_visited', 'ip_address')
    readonly_fields = ('user', 'page_visited', 'timestamp', 'session_key', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        """Activity is auto-generated, not manually added"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Activity cannot be changed"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete activity"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Supervisors can see all activities, customers see only their own"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'supervisor':
            return qs
        return qs.filter(user=request.user)


# Register models
admin.site.register(User, UserAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

# Customize admin site header
admin.site.site_header = "EcoShop Administration"
admin.site.site_title = "EcoShop Admin"
admin.site.index_title = "Welcome to EcoShop Management Panel"

class OrderAdmin(admin.ModelAdmin):
    # ... existing code ...
    
    def save_model(self, request, obj, form, change):
        if change:  # If updating existing order
            old_order = Order.objects.get(pk=obj.pk)
            
            # Check if status changed
            if old_order.status != obj.status:
                if obj.status == 'shipped':
                    send_order_shipped_email(obj)
                elif obj.status == 'delivered':
                    send_order_delivered_email(obj)
        
        super().save_model(request, obj, form, change)