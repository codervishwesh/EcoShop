from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
import uuid
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .forms import CheckoutForm
from accounts.views import track_user_activity
from core.emails import send_order_confirmation_email


def get_or_create_cart(request):
    """
    Helper function to get or create cart for user or session
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        request.session['cart_session_key'] = session_key
    
    return cart


def cart_view(request):
    """
    Shopping Cart View
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.all().select_related('product')
    
    # Track user activity
    if request.user.is_authenticated:
        track_user_activity(request, 'Shopping Cart')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.total_price,
        'total_items': cart.total_items,
        'total_eco_points': cart.total_eco_points,
    }
    return render(request, 'orders/cart.html', context)


def add_to_cart(request, product_id):
    """
    Add product to cart
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock
    if product.stock < quantity:
        messages.error(request, f'Sorry, only {product.stock} items available in stock!')
        return redirect('products:product_detail', slug=product.slug)
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Updated {product.name} quantity in cart!')
    else:
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


def update_cart(request, item_id):
    """
    Update cart item quantity
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    action = request.POST.get('action')
    
    if action == 'increase':
        if cart_item.product.stock > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            messages.error(request, 'Maximum stock reached!')
    
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.info(request, 'Item removed from cart!')
    
    return redirect('orders:cart')


def remove_from_cart(request, item_id):
    """
    Remove item from cart
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('orders:cart')


@login_required
def checkout_view(request):
    """
    Checkout View
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.all().select_related('product')
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('products:product_list')
    
    # Check stock availability
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f'{item.product.name} is out of stock!')
            return redirect('orders:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order with transaction
            with transaction.atomic():
                # Create order
                order = form.save(commit=False)
                order.user = request.user
                order.order_number = f'ECO-{uuid.uuid4().hex[:8].upper()}'
                order.subtotal = cart.total_price
                order.tax = cart.total_price * Decimal('0.13')  # 13% tax
                order.shipping_cost = Decimal('5.00') if cart.total_price < 50 else Decimal('0.00')
                order.total = order.subtotal + order.tax + order.shipping_cost
                order.eco_points_earned = cart.total_eco_points
                order.co2_saved = Decimal(str(cart.total_eco_points * 0.01))  # 0.01 kg per point
                order.save()
                
                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.name,
                        product_price=cart_item.product.price,
                        quantity=cart_item.quantity,
                        eco_score=cart_item.product.eco_score
                    )
                    
                    # Update product stock
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                
                # Update user eco metrics
                user = request.user
                user.eco_points += order.eco_points_earned
                user.total_orders += 1
                user.co2_saved += order.co2_saved
                user.save()
                
                # Clear cart
                cart.items.all().delete()
                
                # Send order confirmation email
                try:
                    send_order_confirmation_email(order)
                except Exception as e:
                    print(f"Email sending failed: {e}")
                
                messages.success(request, f'Order placed successfully! Order #{order.order_number}. Check your email for confirmation.')
                return redirect('orders:order_confirmation', order_number=order.order_number)
    else:
        # Pre-fill form with user data
        initial_data = {
            'shipping_name': request.user.get_full_name(),
            'shipping_email': request.user.email,
            'shipping_phone': request.user.phone,
            'shipping_address': request.user.address,
            'shipping_city': request.user.city,
            'shipping_country': request.user.country,
            'shipping_postal_code': request.user.postal_code,
        }
        form = CheckoutForm(initial=initial_data)
    
    # Track user activity
    track_user_activity(request, 'Checkout')
    
    # Calculate totals
    subtotal = cart.total_price
    tax = subtotal * Decimal('0.13')
    shipping = Decimal('5.00') if subtotal < 50 else Decimal('0.00')
    total = subtotal + tax + shipping
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
        'eco_points': cart.total_eco_points,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_confirmation_view(request, order_number):
    """
    Order Confirmation View
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Track user activity
    track_user_activity(request, f'Order Confirmation: {order_number}')
    
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def order_history_view(request):
    """
    Order History View
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Track user activity
    track_user_activity(request, 'Order History')
    
    context = {
        'orders': orders
    }
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail_view(request, order_number):
    """
    Order Detail View
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Track user activity
    track_user_activity(request, f'Order Detail: {order_number}')
    
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    return render(request, 'orders/order_detail.html', context)