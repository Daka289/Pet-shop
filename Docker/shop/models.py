from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os


class Category(models.Model):
    """Product categories for pets and pet supplies"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category_detail', args=[self.slug])


class Product(models.Model):
    """Products in the pet shop"""
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    stock_quantity = models.PositiveIntegerField(default=0)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='in_stock')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='Weight in kg')
    brand = models.CharField(max_length=100, blank=True)
    age_group = models.CharField(max_length=50, blank=True, help_text='e.g., Puppy, Adult, Senior')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            try:
                # Check if the image file exists before trying to open it
                if hasattr(self.image, 'path') and os.path.exists(self.image.path):
                    img = Image.open(self.image.path)
                    if img.height > 500 or img.width > 500:
                        output_size = (500, 500)
                        img.thumbnail(output_size)
                        img.save(self.image.path)
            except (FileNotFoundError, OSError):
                # Handle cases where image file doesn't exist or can't be processed
                pass

    @property
    def get_price(self):
        """Return discount price if available, otherwise regular price"""
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0


class ProductImage(models.Model):
    """Additional images for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - Image"


class Review(models.Model):
    """Product reviews by customers"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user.username}"


class Cart(models.Model):
    """Shopping cart for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Calculate total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.quantity * self.product.get_price


class Wishlist(models.Model):
    """User wishlist"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}" 