from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from shop.models import Cart
from .models import Order, OrderItem
import uuid


@login_required
def checkout(request):
    """Checkout view"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_detail')

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_detail')

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            total_amount=cart.total_price,
            shipping_address=request.POST.get('shipping_address'),
            billing_address=request.POST.get('billing_address'),
            phone_number=request.POST.get('phone_number'),
            email=request.POST.get('email'),
            notes=request.POST.get('notes', ''),
        )

        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.get_price,
            )

        # Clear cart
        cart_items.delete()

        messages.success(request, f'Order {order.order_number} placed successfully!')
        return redirect('orders:order_detail', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_list(request):
    """List user orders"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context) 