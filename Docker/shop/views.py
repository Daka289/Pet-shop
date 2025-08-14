from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.utils import timezone
import uuid
from .models import Product, Category, Cart, CartItem, Wishlist, Review
from .forms import ReviewForm
from orders.models import Order, OrderItem
from accounts.models import UserProfile


def home(request):
    """Home page view"""
    # Cache featured products for better performance
    featured_products = cache.get('featured_products')
    if not featured_products:
        featured_products = Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category')[:8]
        cache.set('featured_products', featured_products, 300)  # Cache for 5 minutes
    
    categories = Category.objects.all()[:6]
    
    # Get user's wishlist products if authenticated
    user_wishlist_products = []
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            user_wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'user_wishlist_products': user_wishlist_products,
    }
    return render(request, 'shop/home.html', context)


def product_list(request):
    """Product listing with filtering and pagination"""
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    
    # Filtering
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's wishlist products if authenticated
    user_wishlist_products = []
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            user_wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
        'user_wishlist_products': user_wishlist_products,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, slug):
    """Product detail view with reviews"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('reviews__user', 'images'),
        slug=slug,
        is_active=True
    )
    
    # Get all reviews for rating calculation
    all_reviews = product.reviews.all()
    average_rating = all_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get latest 5 reviews for display
    reviews = all_reviews[:5]
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Review form for authenticated users
    review_form = None
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
        except Review.DoesNotExist:
            review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
        'related_products': related_products,
        'review_form': review_form,
        'user_review': user_review,
    }
    return render(request, 'shop/product_detail.html', context)


def category_detail(request, slug):
    """Category detail view"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'shop/category_detail.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if product.stock_quantity < quantity:
        messages.error(request, 'Not enough stock available.')
        return redirect('shop:product_detail', slug=product.slug)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('shop:cart_detail')


@login_required
def cart_detail(request):
    """Shopping cart detail"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart_detail.html', context)


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    else:
        if cart_item.product.stock_quantity < quantity:
            messages.error(request, 'Not enough stock available.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
    
    return redirect('shop:cart_detail')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart.')
    return redirect('shop:cart_detail')


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """Add/remove product to/from wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.success(request, f'{product.name} removed from wishlist.')
        in_wishlist = False
    else:
        wishlist.products.add(product)
        messages.success(request, f'{product.name} added to wishlist!')
        in_wishlist = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})
    
    return redirect('shop:product_detail', slug=product.slug)


@login_required
def wishlist_detail(request):
    """Wishlist detail"""
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        products = wishlist.products.filter(is_active=True)
    except Wishlist.DoesNotExist:
        products = []
    
    context = {
        'products': products,
    }
    return render(request, 'shop/wishlist_detail.html', context)


@login_required
@require_POST
def add_review(request, product_id):
    """Add product review"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('shop:product_detail', slug=product.slug)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, 'Your review has been added!')
    else:
        messages.error(request, 'Please correct the errors in your review.')
    
    return redirect('shop:product_detail', slug=product.slug)


@login_required
def checkout(request):
    """Checkout page view"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_detail')
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_detail')
    
    # Get user profile for pre-filling form
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'profile': profile,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
@require_POST
def process_checkout(request):
    """Process checkout and create order"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart not found'})
    
    if not cart_items:
        return JsonResponse({'success': False, 'error': 'Cart is empty'})
    
    # Generate unique order number
    order_number = f"PET-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create shipping address string
    shipping_address = f"{request.POST.get('first_name')} {request.POST.get('last_name')}\n"
    shipping_address += f"{request.POST.get('address')}\n"
    shipping_address += f"{request.POST.get('city')}, {request.POST.get('postal_code')}\n"
    shipping_address += f"{request.POST.get('country')}"
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        total_amount=cart.total_price,
        shipping_address=shipping_address,
        billing_address=shipping_address,  # Same as shipping for simplicity
        phone_number=request.POST.get('phone'),
        email=request.POST.get('email'),
        notes=request.POST.get('notes', ''),
        status='processing'
    )
    
    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.get_price
        )
        
        # Update product stock
        product = cart_item.product
        product.stock_quantity -= cart_item.quantity
        product.save()
    
    # Clear the cart
    cart_items.delete()
    
    return JsonResponse({
        'success': True, 
        'order_number': order_number,
        'message': 'Order placed successfully!'
    })


@login_required
def order_confirmation(request):
    """Order confirmation page"""
    order_number = request.GET.get('order')
    if not order_number:
        messages.error(request, 'Order not found.')
        return redirect('shop:home')
    
    try:
        order = Order.objects.get(
            order_number=order_number,
            user=request.user
        )
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('shop:home')
    
    context = {
        'order': order,
    }
    return render(request, 'shop/order_confirmation.html', context) 