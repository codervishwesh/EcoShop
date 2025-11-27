from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    
    # Order History
    path('orders/', views.order_history_view, name='order_history'),
    path('order/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
