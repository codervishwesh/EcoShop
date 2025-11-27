from orders.models import Cart

def cart_count(request):
    """
    Context processor to make cart count available in all templates
    """
    cart_count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0
    elif 'cart_session_key' in request.session:
        try:
            cart = Cart.objects.get(session_key=request.session['cart_session_key'])
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            cart_count = 0
    
    return {
        'cart_count': cart_count
    }
