from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product
from decimal import Decimal
from django.core.files import File
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories_data = [
            {'name': 'Dog Food', 'slug': 'dog-food', 'description': 'Premium dog food for all breeds and ages', 'image_file': 'dog_food.jpg'},
            {'name': 'Cat Food', 'slug': 'cat-food', 'description': 'Nutritious cat food for healthy cats', 'image_file': 'cat_food.jpg'},
            {'name': 'Dog Toys', 'slug': 'dog-toys', 'description': 'Fun and safe toys for dogs', 'image_file': 'dog_toys.jpg'},
            {'name': 'Cat Toys', 'slug': 'cat-toys', 'description': 'Interactive toys for cats', 'image_file': 'cat_toys.jpg'},
            {'name': 'Pet Accessories', 'slug': 'pet-accessories', 'description': 'Collars, leashes, and more', 'image_file': 'accessories.jpg'},
            {'name': 'Pet Care', 'slug': 'pet-care', 'description': 'Grooming and health care products', 'image_file': 'pet_care.jpg'},
        ]

        for cat_data in categories_data:
            image_file = cat_data.pop('image_file', None)
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            # Add image if category was created and image file exists
            if created and image_file:
                image_path = os.path.join(settings.BASE_DIR, 'media', 'categories', image_file)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        category.image.save(image_file, File(f), save=True)
                        
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create products
        products_data = [
            {
                'name': 'Premium Dry Dog Food - Chicken & Rice',
                'slug': 'premium-dry-dog-food-chicken-rice',
                'category': 'dog-food',
                'description': 'High-quality dry dog food made with real chicken and brown rice. Perfect for adult dogs of all sizes.',
                'price': Decimal('45.99'),
                'discount_price': Decimal('39.99'),
                'stock_quantity': 50,
                'brand': 'PetNutrition',
                'age_group': 'Adult',
                'is_featured': True,
                'weight': Decimal('15.0'),
                'image_file': 'premium_dry_dog_food_chicken_rice.png',
            },
            {
                'name': 'Grain-Free Cat Food - Salmon',
                'slug': 'grain-free-cat-food-salmon',
                'category': 'cat-food',
                'description': 'Grain-free cat food with real salmon. Rich in omega-3 fatty acids for healthy skin and coat.',
                'price': Decimal('32.99'),
                'stock_quantity': 30,
                'brand': 'FelineHealth',
                'age_group': 'Adult',
                'is_featured': True,
                'weight': Decimal('5.0'),
                'image_file': 'grain_free_cat_food_salmon.png',
            },
            {
                'name': 'Interactive Rope Dog Toy',
                'slug': 'interactive-rope-toy',
                'category': 'dog-toys',
                'description': 'Durable rope toy perfect for playing tug-of-war and keeping teeth clean.',
                'price': Decimal('12.99'),
                'stock_quantity': 75,
                'brand': 'PlayTime',
                'is_featured': True,
                'weight': Decimal('0.3'),
                'image_file': 'interactive_rope_dog_toy.png',
            },
            {
                'name': 'Feather Wand Cat Toy',
                'slug': 'feather-wand-cat-toy',
                'category': 'cat-toys',
                'description': 'Interactive feather wand that will keep your cat entertained for hours.',
                'price': Decimal('8.99'),
                'stock_quantity': 60,
                'brand': 'CatPlay',
                'weight': Decimal('0.1'),
                'image_file': 'feather_wand_cat_toy.png',
            },
            {
                'name': 'Adjustable Dog Collar',
                'slug': 'adjustable-dog-collar',
                'category': 'pet-accessories',
                'description': 'Comfortable and adjustable collar suitable for medium to large dogs.',
                'price': Decimal('15.99'),
                'discount_price': Decimal('12.99'),
                'stock_quantity': 40,
                'brand': 'PetComfort',
                'weight': Decimal('0.2'),
                'image_file': 'dog_collar.png',
            },
            {
                'name': 'Pet Shampoo - Oatmeal & Honey',
                'slug': 'pet-shampoo-oatmeal-honey',
                'category': 'pet-care',
                'description': 'Gentle shampoo with oatmeal and honey for sensitive skin.',
                'price': Decimal('18.99'),
                'stock_quantity': 25,
                'brand': 'CleanPaws',
                'weight': Decimal('0.5'),
                'image_file': 'pet_shampoo_oatmeal_honey.png',
            },
            {
                'name': 'Puppy Training Treats',
                'slug': 'puppy-training-treats',
                'category': 'dog-food',
                'description': 'Small, soft treats perfect for training puppies. Made with real chicken.',
                'price': Decimal('9.99'),
                'stock_quantity': 80,
                'brand': 'PuppyTrain',
                'age_group': 'Puppy',
                'is_featured': True,
                'weight': Decimal('0.4'),
                'image_file': 'puppy_training_treats.png',
            },
            {
                'name': 'Cat Scratching Post',
                'slug': 'cat-scratching-post',
                'category': 'cat-toys',
                'description': 'Tall scratching post covered in sisal rope. Perfect for cats to scratch and climb.',
                'price': Decimal('29.99'),
                'stock_quantity': 20,
                'brand': 'CatFurniture',
                'weight': Decimal('3.0'),
                'image_file': 'car_scratching_post.png',
            },
        ]

        for product_data in products_data:
            try:
                category = Category.objects.get(slug=product_data['category'])
                product_data['category'] = category
                image_file = product_data.pop('image_file', None)
                
                product, created = Product.objects.get_or_create(
                    slug=product_data['slug'],
                    defaults=product_data
                )
                
                # Add image if product was created and image file exists
                if created and image_file:
                    # Try multiple possible image locations
                    image_paths = [
                        os.path.join(settings.BASE_DIR, 'media', 'products', image_file),
                        os.path.join(settings.BASE_DIR, 'images', image_file),
                        os.path.join('/app/media/products', image_file),
                        os.path.join('/app/images', image_file),
                    ]
                    
                    image_found = False
                    for image_path in image_paths:
                        if os.path.exists(image_path):
                            # Copy image to the correct media location if needed
                            target_path = os.path.join(settings.MEDIA_ROOT, 'products', image_file)
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            if image_path != target_path:
                                import shutil
                                try:
                                    shutil.copy2(image_path, target_path)
                                    self.stdout.write(f'Copied image: {image_file}')
                                except Exception as e:
                                    self.stdout.write(f'Failed to copy image {image_file}: {e}')
                                    continue
                            
                            # Assign image to product
                            product.image = f'products/{image_file}'
                            product.save()
                            image_found = True
                            self.stdout.write(f'Assigned image to {product.name}: {image_file}')
                            break
                    
                    if not image_found:
                        self.stdout.write(f'Image not found for {product.name}: {image_file}')
                        # Still assign the image path even if file doesn't exist - Django will handle it gracefully now
                        product.image = f'products/{image_file}'
                        product.save()
                
                if created:
                    self.stdout.write(f'Created product: {product.name}')
            except Category.DoesNotExist:
                self.stdout.write(f'Category not found: {product_data["category"]}')

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@petshop.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write('Created admin user (admin/admin123)')

        # Create test users
        test_users = [
            {'username': 'danilot', 'email': 'danilo@example.com', 'first_name': 'Danilo', 'last_name': 'T'},
            {'username': 'andrijat', 'email': 'andrija@example.com', 'first_name': 'Andrija', 'last_name': 'T'},
        ]

        for user_data in test_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    password='test123',
                    **user_data
                )
                self.stdout.write(f'Created test user: {user_data["username"]}')

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data!')) 