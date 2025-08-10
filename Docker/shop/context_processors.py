from .models import Cart


def cart_context(request):
    """Add cart information to all templates"""
    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.total_items
        except Cart.DoesNotExist:
            cart_items_count = 0
    
    return {
        'cart_items_count': cart_items_count,
    } 