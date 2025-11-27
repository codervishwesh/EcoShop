from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.core.paginator import Paginator
from datetime import timedelta
from decimal import Decimal

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CustomPasswordResetForm
from .models import User, UserActivity
from .decorators import admin_required, supervisor_required, staff_required
from orders.models import Order, OrderItem
from products.models import Product, Category, Review
from django.contrib.auth import logout
from core.emails import send_welcome_email

# ==================== AUTHENTICATION VIEWS ====================

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        user.role = User.ROLE_CUSTOMER
        user.save()
        
        # Send welcome email
        send_welcome_email(user)
        
        messages.success(self.request, 'Account created successfully! Please check your email.')
        return response

class UserLoginView(LoginView):
    """
    User Login View - Handles authentication
    """
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Welcome back, {user.username}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        if user.is_admin():
            return reverse_lazy('accounts:management_dashboard')
        elif user.is_supervisor():
            return reverse_lazy('accounts:management_dashboard')
        return reverse_lazy('accounts:dashboard')


class UserLogoutView(LogoutView):
    next_page = 'core:home'
    http_method_names = ['get', 'post']  # Allow GET requests
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

# ==================== CUSTOMER VIEWS ====================

@login_required
def profile_view(request):
    """
    User Profile View - Edit personal information
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def dashboard_view(request):
    """
    Customer Dashboard - Shows eco metrics and recent orders
    """
    user = request.user
    
    # Redirect staff to management dashboard
    if user.is_staff_member():
        return redirect('accounts:management_dashboard')
    
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    total_spent = Order.objects.filter(user=user).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Eco impact calculations
    trees_planted = user.eco_points // 50
    plastic_avoided = user.total_orders * 34  # grams
    water_saved = user.total_orders * 4.5  # liters
    
    context = {
        'user': user,
        'recent_orders': recent_orders,
        'total_spent': total_spent,
        'trees_planted': trees_planted,
        'plastic_avoided': plastic_avoided,
        'water_saved': water_saved,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def user_history_view(request):
    """
    User History - Shows page visit tracking
    """
    activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)
    
    context = {
        'activities': activities,
        'visits_today': activities.filter(timestamp__date=today).count(),
        'visits_this_week': activities.filter(timestamp__gte=week_ago).count(),
        'visits_this_month': activities.filter(timestamp__gte=month_ago).count(),
        'total_visits': activities.count(),
    }
    return render(request, 'accounts/user_history.html', context)


class CustomPasswordResetView(PasswordResetView):
    """
    Custom Password Reset View
    """
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset email has been sent!')
        return super().form_valid(form)


# ==================== MANAGEMENT DASHBOARD (ADMIN & SUPERVISOR) ====================

@staff_required
def management_dashboard(request):
    """
    Management Dashboard - For Admin and Supervisor
    Shows different stats based on role
    """
    user = request.user
    
    # Common statistics
    stats = {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_customers': User.objects.filter(role=User.ROLE_CUSTOMER).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue': Order.objects.aggregate(total=Sum('total'))['total'] or Decimal('0.00'),
        'avg_eco_score': Product.objects.aggregate(avg=Avg('eco_score'))['avg'] or 0,
    }
    
    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Recent reviews (for moderation)
    recent_reviews = Review.objects.select_related('user', 'product').order_by('-created_at')[:5]
    
    # Low stock products (stock < 10)
    low_stock_products = Product.objects.filter(stock__lt=10, is_active=True).order_by('stock')[:5]
    
    # Admin-only statistics
    if user.is_admin():
        stats['total_supervisors'] = User.objects.filter(role=User.ROLE_SUPERVISOR).count()
        stats['total_admins'] = User.objects.filter(role=User.ROLE_ADMIN).count()
        stats['total_categories'] = Category.objects.count()
        stats['total_reviews'] = Review.objects.count()
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'low_stock_products': low_stock_products,
        'is_admin': user.is_admin(),
        'is_supervisor': user.is_supervisor(),
    }
    return render(request, 'accounts/management/dashboard.html', context)


# ==================== USER MANAGEMENT (ADMIN ONLY) ====================

@admin_required
def user_list_view(request):
    """
    User List - Admin can see all users
    """
    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')
    
    users = User.objects.all().order_by('-created_at')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if search:
        users = users.filter(
            username__icontains=search
        ) | users.filter(
            email__icontains=search
        ) | users.filter(
            first_name__icontains=search
        ) | users.filter(
            last_name__icontains=search
        )
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search': search,
        'roles': User.ROLE_CHOICES,
    }
    return render(request, 'accounts/management/user_list.html', context)


@admin_required
def user_detail_view(request, pk):
    """
    User Detail - View and edit user
    """
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'change_role':
            new_role = request.POST.get('role')
            if new_role in [User.ROLE_ADMIN, User.ROLE_SUPERVISOR, User.ROLE_CUSTOMER]:
                user_obj.role = new_role
                user_obj.save()
                messages.success(request, f'Role changed to {user_obj.get_role_display()}')
        
        elif action == 'toggle_active':
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            status = 'activated' if user_obj.is_active else 'deactivated'
            messages.success(request, f'User {status}')
        
        elif action == 'delete':
            if user_obj != request.user:  # Can't delete yourself
                user_obj.delete()
                messages.success(request, 'User deleted successfully')
                return redirect('accounts:user_list')
            else:
                messages.error(request, 'You cannot delete your own account')
        
        return redirect('accounts:user_detail', pk=pk)
    
    # User statistics
    user_orders = Order.objects.filter(user=user_obj)
    user_reviews = Review.objects.filter(user=user_obj)
    
    context = {
        'user_obj': user_obj,
        'user_orders': user_orders[:5],
        'user_reviews': user_reviews[:5],
        'total_orders': user_orders.count(),
        'total_reviews': user_reviews.count(),
        'total_spent': user_orders.aggregate(total=Sum('total'))['total'] or Decimal('0.00'),
        'roles': User.ROLE_CHOICES,
    }
    return render(request, 'accounts/management/user_detail.html', context)


@admin_required
def create_staff_user(request):
    """
    Create Staff User - Admin can create new admin/supervisor accounts
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        elif role not in [User.ROLE_ADMIN, User.ROLE_SUPERVISOR]:
            messages.error(request, 'Invalid role selected')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, f'{role.title()} account created successfully!')
            return redirect('accounts:user_list')
    
    context = {
        'staff_roles': [
            (User.ROLE_ADMIN, 'Admin'),
            (User.ROLE_SUPERVISOR, 'Supervisor'),
        ]
    }
    return render(request, 'accounts/management/create_staff.html', context)


# ==================== PRODUCT MANAGEMENT ====================

@staff_required
def product_management_list(request):
    """
    Product Management - List all products
    Admin and Supervisor can view
    """
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    stock_filter = request.GET.get('stock', '')
    
    products = Product.objects.select_related('category', 'seller').order_by('-created_at')
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    if search:
        products = products.filter(name__icontains=search)
    
    if stock_filter == 'low':
        products = products.filter(stock__lt=10)
    elif stock_filter == 'out':
        products = products.filter(stock=0)
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': Category.objects.all(),
        'category_filter': category_filter,
        'search': search,
        'stock_filter': stock_filter,
        'can_delete': request.user.is_admin(),
    }
    return render(request, 'accounts/management/product_list.html', context)


@staff_required
def product_management_edit(request, pk):
    """
    Product Edit - Admin and Supervisor can edit
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.price = Decimal(request.POST.get('price', product.price))
        product.stock = int(request.POST.get('stock', product.stock))
        product.eco_score = int(request.POST.get('eco_score', product.eco_score))
        product.is_active = request.POST.get('is_active') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        
        category_id = request.POST.get('category')
        if category_id:
            product.category = get_object_or_404(Category, pk=category_id)
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('accounts:product_management_list')
    
    context = {
        'product': product,
        'categories': Category.objects.all(),
    }
    return render(request, 'accounts/management/product_edit.html', context)


@admin_required
def product_management_delete(request, pk):
    """
    Product Delete - Admin only
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('accounts:product_management_list')
    
    return render(request, 'accounts/management/product_delete.html', {'product': product})


# ==================== ORDER MANAGEMENT ====================

@staff_required
def order_management_list(request):
    """
    Order Management - List all orders
    """
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search:
        orders = orders.filter(
            order_number__icontains=search
        ) | orders.filter(
            user__username__icontains=search
        ) | orders.filter(
            shipping_email__icontains=search
        )
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES if hasattr(Order, 'STATUS_CHOICES') else [
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        'can_delete': request.user.is_admin(),
    }
    return render(request, 'accounts/management/order_list.html', context)


@staff_required
def order_management_detail(request, pk):
    """
    Order Detail - View and update order status
    """
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
                order.status = new_status
                order.save()
                messages.success(request, f'Order status updated to {order.get_status_display()}')
        
        elif action == 'delete' and request.user.is_admin():
            order.delete()
            messages.success(request, 'Order deleted successfully')
            return redirect('accounts:order_management_list')
        
        return redirect('accounts:order_management_detail', pk=pk)
    
    context = {
        'order': order,
        'order_items': order_items,
        'can_delete': request.user.is_admin(),
        'status_choices': [
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
    }
    return render(request, 'accounts/management/order_detail.html', context)


# ==================== REVIEW MANAGEMENT ====================

@staff_required
def review_management_list(request):
    """
    Review Management - Moderate reviews
    """
    approval_filter = request.GET.get('approved', '')
    
    reviews = Review.objects.select_related('user', 'product').order_by('-created_at')
    
    if approval_filter == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif approval_filter == 'pending':
        reviews = reviews.filter(is_approved=False)
    
    paginator = Paginator(reviews, 20)
    page = request.GET.get('page', 1)
    reviews = paginator.get_page(page)
    
    context = {
        'reviews': reviews,
        'approval_filter': approval_filter,
        'can_delete': request.user.is_admin(),
    }
    return render(request, 'accounts/management/review_list.html', context)


@staff_required
def review_toggle_approval(request, pk):
    """
    Toggle Review Approval - Admin and Supervisor
    """
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = not review.is_approved
    review.save()
    
    status = 'approved' if review.is_approved else 'hidden'
    messages.success(request, f'Review {status}')
    return redirect('accounts:review_management_list')


@admin_required
def review_delete(request, pk):
    """
    Delete Review - Admin only
    """
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully')
        return redirect('accounts:review_management_list')
    
    return render(request, 'accounts/management/review_delete.html', {'review': review})


# ==================== REPORTS (ADMIN ONLY) ====================

@admin_required
def reports_view(request):
    """
    Reports Dashboard - Admin only
    """
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Orders statistics
    orders_in_range = Order.objects.filter(created_at__gte=start_date)
    
    stats = {
        'total_orders': orders_in_range.count(),
        'total_revenue': orders_in_range.aggregate(total=Sum('total'))['total'] or Decimal('0.00'),
        'total_eco_points': orders_in_range.aggregate(total=Sum('eco_points_earned'))['total'] or 0,
        'total_co2_saved': orders_in_range.aggregate(total=Sum('co2_saved'))['total'] or Decimal('0.00'),
        'avg_order_value': orders_in_range.aggregate(avg=Avg('total'))['avg'] or Decimal('0.00'),
    }
    
    # Orders by status
    orders_by_status = orders_in_range.values('status').annotate(count=Count('id'))
    
    # Top products
    top_products = OrderItem.objects.filter(
        order__created_at__gte=start_date
    ).values('product_name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:10]
    
    # New users
    new_users = User.objects.filter(
        created_at__gte=start_date,
        role=User.ROLE_CUSTOMER
    ).count()
    
    context = {
        'stats': stats,
        'orders_by_status': orders_by_status,
        'top_products': top_products,
        'new_users': new_users,
        'days': days,
    }
    return render(request, 'accounts/management/reports.html', context)


# ==================== HELPER FUNCTIONS ====================

def track_user_activity(request, page_name):
    """
    Helper function to track user activity
    """
    if request.user.is_authenticated:
        UserActivity.objects.create(
            user=request.user,
            page_visited=page_name,
            session_key=request.session.session_key,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
