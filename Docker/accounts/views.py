from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile
from shop.models import Wishlist
from orders.models import Order


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('shop:home')


def user_register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def user_profile(request):
    """User profile view with wishlist and orders"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Handle profile form submission
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        # Handle user fields
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.save()
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user's wishlist
    wishlist_products = []
    wishlist_count = 0
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist_products = wishlist.products.filter(is_active=True).select_related('category')[:12]
        wishlist_count = wishlist.products.filter(is_active=True).count()
    except Wishlist.DoesNotExist:
        pass
    
    # Get user's orders
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')[:10]
    orders_count = Order.objects.filter(user=request.user).count()
    
    context = {
        'form': form,
        'profile': profile,
        'wishlist_products': wishlist_products,
        'wishlist_count': wishlist_count,
        'orders': orders,
        'orders_count': orders_count,
    }
    return render(request, 'accounts/profile.html', context) 