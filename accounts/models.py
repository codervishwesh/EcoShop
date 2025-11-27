from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model with Role-Based Access Control (RBAC)
    
    Roles:
    - admin: Full access to everything (is_superuser=True, is_staff=True)
    - supervisor: Limited admin access (is_staff=True)
    - customer: Can only shop and manage own data (is_staff=False)
    """
    
    # Role Choices
    ROLE_ADMIN = 'admin'
    ROLE_SUPERVISOR = 'supervisor'
    ROLE_CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_SUPERVISOR, 'Supervisor'),
        (ROLE_CUSTOMER, 'Customer'),
    ]
    
    # Role field
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        help_text='User role determines access permissions'
    )
    
    # Contact & Address
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Eco-related fields
    eco_points = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    co2_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # User type (for sellers - kept for backward compatibility)
    is_seller = models.BooleanField(default=False)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ========== ROLE HELPER METHODS ==========
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == self.ROLE_ADMIN
    
    def is_supervisor(self):
        """Check if user is a supervisor"""
        return self.role == self.ROLE_SUPERVISOR
    
    def is_customer(self):
        """Check if user is a customer"""
        return self.role == self.ROLE_CUSTOMER
    
    def is_staff_member(self):
        """Check if user is admin or supervisor (has staff access)"""
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def get_role_display_badge(self):
        """Return HTML badge for role display"""
        badges = {
            self.ROLE_ADMIN: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Admin</span>',
            self.ROLE_SUPERVISOR: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">Supervisor</span>',
            self.ROLE_CUSTOMER: '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Customer</span>',
        }
        return badges.get(self.role, '')
    
    # ========== PERMISSION HELPER METHODS ==========
    
    # Product Permissions
    def can_view_all_products(self):
        return True  # Everyone can view products
    
    def can_create_product(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_edit_product(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_delete_product(self):
        return self.role == self.ROLE_ADMIN
    
    # Category Permissions
    def can_manage_categories(self):
        return self.role == self.ROLE_ADMIN
    
    # Order Permissions
    def can_view_all_orders(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_update_order_status(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_delete_order(self):
        return self.role == self.ROLE_ADMIN
    
    # User Permissions
    def can_view_all_users(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_manage_users(self):
        return self.role == self.ROLE_ADMIN
    
    def can_assign_roles(self):
        return self.role == self.ROLE_ADMIN
    
    # Review Permissions
    def can_moderate_reviews(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_delete_any_review(self):
        return self.role == self.ROLE_ADMIN
    
    # Report Permissions
    def can_view_reports(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def can_view_all_reports(self):
        return self.role == self.ROLE_ADMIN
    
    # Settings Permissions
    def can_manage_settings(self):
        return self.role == self.ROLE_ADMIN
    
    # Admin Panel Access
    def can_access_admin_panel(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set is_staff and is_superuser based on role
        """
        if self.role == self.ROLE_ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.ROLE_SUPERVISOR:
            self.is_staff = True
            self.is_superuser = False
        else:  # ROLE_CUSTOMER
            self.is_staff = False
            self.is_superuser = False
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']


class UserActivity(models.Model):
    """
    Track user activity for the User History feature
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    page_visited = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.page_visited} at {self.timestamp}"
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
