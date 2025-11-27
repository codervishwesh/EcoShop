from django.shortcuts import render
from products.models import Product, Category
from accounts.models import User
from orders.models import Order
from accounts.views import track_user_activity
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .chatbot import EcoShopChatbot 


def home_view(request):
    """
    Home Page View
    """
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:6]
    
    # Get all categories
    categories = Category.objects.all()[:6]
    
    # Calculate statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_users = User.objects.filter(is_active=True).count()
    total_sellers = User.objects.filter(is_seller=True, is_active=True).count()
    
    # Calculate average eco score
    from django.db.models import Avg
    avg_eco_score = Product.objects.filter(is_active=True).aggregate(Avg('eco_score'))['eco_score__avg'] or 0
    
    # Track user activity
    if request.user.is_authenticated:
        track_user_activity(request, 'Home Page')
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'total_products': total_products,
        'total_users': total_users,
        'total_sellers': total_sellers,
        'avg_eco_score': round(avg_eco_score, 1),
    }
    return render(request, 'home.html', context)


def about_view(request):
    """
    About Us Page
    """
    if request.user.is_authenticated:
        track_user_activity(request, 'About Us')
    
    return render(request, 'about.html')


def contact_view(request):
    """
    Contact Us Page
    """
    if request.user.is_authenticated:
        track_user_activity(request, 'Contact Us')
    
    if request.method == 'POST':
        # Handle contact form submission
        from django.contrib import messages
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
    
    return render(request, 'contact.html')

@require_POST
def chatbot_response(request):
    """Handle chatbot messages"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        chatbot = EcoShopChatbot(user=request.user if request.user.is_authenticated else None)
        response = chatbot.get_response(message)
        
        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'response': 'Sorry, something went wrong. Please try again!'
        })