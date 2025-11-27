"""
Custom decorators for Role-Based Access Control (RBAC)

Usage:
    @admin_required
    def admin_only_view(request):
        ...
    
    @supervisor_required
    def supervisor_view(request):
        ...
    
    @staff_required
    def staff_view(request):
        ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """
    Decorator that requires user to be an admin.
    Redirects to login if not authenticated.
    Shows 403 Forbidden if authenticated but not admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_admin():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('core:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def supervisor_required(view_func):
    """
    Decorator that requires user to be a supervisor OR admin.
    Admins always have supervisor privileges.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not (request.user.is_admin() or request.user.is_supervisor()):
            messages.error(request, 'Access denied. Supervisor privileges required.')
            return redirect('core:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_required(view_func):
    """
    Decorator that requires user to be staff (admin or supervisor).
    Same as supervisor_required but more explicit naming.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_staff_member():
            messages.error(request, 'Access denied. Staff privileges required.')
            return redirect('core:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def customer_required(view_func):
    """
    Decorator that requires user to be a customer (not staff).
    Useful for customer-only pages like checkout.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        # Staff can also access customer features
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(allowed_roles):
    """
    Decorator that requires user to have one of the allowed roles.
    
    Usage:
        @role_required(['admin', 'supervisor'])
        def some_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to access this page.')
                return redirect('accounts:login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'Access denied. Insufficient privileges.')
                return redirect('core:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def permission_required(permission_method):
    """
    Decorator that checks a specific permission method on the user.
    
    Usage:
        @permission_required('can_delete_product')
        def delete_product_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to access this page.')
                return redirect('accounts:login')
            
            # Get the permission method from the user model
            perm_method = getattr(request.user, permission_method, None)
            if perm_method is None or not callable(perm_method):
                messages.error(request, 'Invalid permission check.')
                return redirect('core:home')
            
            if not perm_method():
                messages.error(request, 'Access denied. You do not have permission to perform this action.')
                return redirect('core:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Mixin classes for Class-Based Views
class AdminRequiredMixin:
    """
    Mixin for class-based views that requires admin role.
    
    Usage:
        class MyView(AdminRequiredMixin, View):
            ...
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_admin():
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('core:home')
        
        return super().dispatch(request, *args, **kwargs)


class SupervisorRequiredMixin:
    """
    Mixin for class-based views that requires supervisor or admin role.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not (request.user.is_admin() or request.user.is_supervisor()):
            messages.error(request, 'Access denied. Supervisor privileges required.')
            return redirect('core:home')
        
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin:
    """
    Mixin for class-based views that requires staff (admin or supervisor) role.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_staff_member():
            messages.error(request, 'Access denied. Staff privileges required.')
            return redirect('core:home')
        
        return super().dispatch(request, *args, **kwargs)
