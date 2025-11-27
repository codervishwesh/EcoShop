from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    """
    Inline for Cart Items
    """
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'added_at', 'get_subtotal')
    
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    get_subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class CartAdmin(admin.ModelAdmin):
    """
    Cart Admin - Read Only
    """
    list_display = ('id', 'user', 'session_key', 'get_total_items', 
                    'get_total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('user', 'session_key', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.total_items
    get_total_items.short_description = 'Items'
    
    def get_total_price(self, obj):
        return f"${obj.total_price:.2f}"
    get_total_price.short_description = 'Total'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class OrderItemInline(admin.TabularInline):
    """
    Inline for Order Items
    """
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'product_price', 
                       'quantity', 'eco_score', 'get_subtotal')
    
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    get_subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class OrderAdmin(admin.ModelAdmin):
    """
    Order Admin with Role-Based Restrictions
    - Admins: Full CRUD + Cancel/Delete
    - Supervisors: View + Update Status Only
    - Customers: No access
    """
    list_display = ('order_number', 'user', 'status_badge', 'total', 
                    'eco_points_earned', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 
                     'shipping_email', 'shipping_name')
    readonly_fields = ('order_number', 'user', 'subtotal', 'tax', 
                       'shipping_cost', 'total', 'eco_points_earned', 
                       'co2_saved', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    list_per_page = 20
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Shipping Information', {
            'fields': ('shipping_name', 'shipping_email', 'shipping_phone',
                       'shipping_address', 'shipping_city', 'shipping_country',
                       'shipping_postal_code'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'total')
        }),
        ('Eco Impact', {
            'fields': ('eco_points_earned', 'co2_saved'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'pending': '#f59e0b',      # yellow
            'processing': '#3b82f6',   # blue
            'shipped': '#8b5cf6',      # purple
            'delivered': '#10b981',    # green
            'cancelled': '#ef4444',    # red
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def get_readonly_fields(self, request, obj=None):
        """Supervisors can only change status"""
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            # Supervisors can only change status, nothing else
            readonly.extend(['shipping_name', 'shipping_email', 'shipping_phone',
                            'shipping_address', 'shipping_city', 'shipping_country',
                            'shipping_postal_code', 'notes'])
        return readonly
    
    def has_add_permission(self, request):
        """Orders are created through checkout, not admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Admins and Supervisors can change orders (status)"""
        return request.user.is_superuser or request.user.role == 'supervisor'
    
    def has_delete_permission(self, request, obj=None):
        """Only Admins can delete orders"""
        return request.user.is_superuser
    
    def get_actions(self, request):
        """Remove delete action for supervisors"""
        actions = super().get_actions(request)
        if not request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    # Custom actions for order management
    @admin.action(description='Mark selected orders as Processing')
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"{queryset.count()} orders marked as Processing.")
    
    @admin.action(description='Mark selected orders as Shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"{queryset.count()} orders marked as Shipped.")
    
    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"{queryset.count()} orders marked as Delivered.")
    
    actions = [mark_processing, mark_shipped, mark_delivered]


class CartItemAdmin(admin.ModelAdmin):
    """
    Cart Item Admin - Read Only
    """
    list_display = ('cart', 'product', 'quantity', 'get_subtotal', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'product__name')
    readonly_fields = ('cart', 'product', 'quantity', 'added_at')
    
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    get_subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class OrderItemAdmin(admin.ModelAdmin):
    """
    Order Item Admin - Read Only
    """
    list_display = ('order', 'product_name', 'product_price', 'quantity', 
                    'eco_score', 'get_subtotal')
    list_filter = ('order__created_at',)
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('order', 'product', 'product_name', 'product_price',
                       'quantity', 'eco_score')
    
    def get_subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    get_subtotal.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Register models
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
