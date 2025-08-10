from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock_quantity', 'stock_status', 'is_featured', 'is_active']
    list_filter = ['category', 'stock_status', 'is_featured', 'is_active', 'created_at']
    list_editable = ['price', 'discount_price', 'stock_quantity', 'stock_status', 'is_featured', 'is_active']
    search_fields = ['name', 'description', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'stock_status')
        }),
        ('Product Details', {
            'fields': ('weight', 'brand', 'age_group')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price']
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    filter_horizontal = ['products']


# Customize admin site header
admin.site.site_header = "Pet Shop Administration"
admin.site.site_title = "Pet Shop Admin"
admin.site.index_title = "Welcome to Pet Shop Administration" 