from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # ==================== CUSTOMER PAGES ====================
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('history/', views.user_history_view, name='history'),
    
    # ==================== PASSWORD RESET ====================
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # ==================== MANAGEMENT DASHBOARD (ADMIN & SUPERVISOR) ====================
    path('management/', views.management_dashboard, name='management_dashboard'),
    path('management/reports/', views.reports_view, name='reports'),
    
    # ==================== USER MANAGEMENT (ADMIN ONLY) ====================
    path('management/users/', views.user_list_view, name='user_list'),
    path('management/users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('management/users/create-staff/', views.create_staff_user, name='create_staff'),
    
    # ==================== PRODUCT MANAGEMENT ====================
    path('management/products/', views.product_management_list, name='product_management_list'),
    path('management/products/<int:pk>/edit/', views.product_management_edit, name='product_management_edit'),
    path('management/products/<int:pk>/delete/', views.product_management_delete, name='product_management_delete'),
    
    # ==================== ORDER MANAGEMENT ====================
    path('management/orders/', views.order_management_list, name='order_management_list'),
    path('management/orders/<int:pk>/', views.order_management_detail, name='order_management_detail'),
    
    # ==================== REVIEW MANAGEMENT ====================
    path('management/reviews/', views.review_management_list, name='review_management_list'),
    path('management/reviews/<int:pk>/toggle/', views.review_toggle_approval, name='review_toggle_approval'),
    path('management/reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
]
