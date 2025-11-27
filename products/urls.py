from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product List
    path('', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='category_products'),
    
    # Product Detail
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Search
    path('search/', views.product_search_view, name='search'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # ADD THIS
    
    # Reviews
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    
    # Product Management (For Sellers)
    path('create/', views.product_create_view, name='product_create'),
    path('update/<slug:slug>/', views.product_update_view, name='product_update'),
]