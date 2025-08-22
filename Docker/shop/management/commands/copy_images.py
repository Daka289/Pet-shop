from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = 'Copy product images to media directory'

    def handle(self, *args, **options):
        self.stdout.write('Copying product images...')

        # Ensure media directories exist
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_products_dir, exist_ok=True)
        
        # Possible source directories
        source_dirs = [
            '/app/images',
            os.path.join(settings.BASE_DIR, 'images'),
            os.path.join(settings.BASE_DIR, 'media', 'products'),
        ]
        
        images_copied = 0
        
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                self.stdout.write(f'Found source directory: {source_dir}')
                
                # Copy all image files
                for filename in os.listdir(source_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        source_path = os.path.join(source_dir, filename)
                        target_path = os.path.join(media_products_dir, filename)
                        
                        try:
                            shutil.copy2(source_path, target_path)
                            self.stdout.write(f'Copied: {filename}')
                            images_copied += 1
                        except Exception as e:
                            self.stdout.write(f'Failed to copy {filename}: {e}')
                
                # Don't copy from multiple directories
                if images_copied > 0:
                    break
        
        if images_copied == 0:
            self.stdout.write('No images found to copy')
            self.stdout.write('Searching for image files...')
            
            # Search for PNG files anywhere in the app
            for root, dirs, files in os.walk('/app'):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        full_path = os.path.join(root, file)
                        self.stdout.write(f'Found: {full_path}')
        
        # List final contents
        if os.path.exists(media_products_dir):
            files_in_media = os.listdir(media_products_dir)
            self.stdout.write(f'Media directory contents ({len(files_in_media)} files):')
            for file in files_in_media:
                self.stdout.write(f'  - {file}')
        
        self.stdout.write(self.style.SUCCESS(f'Image copying complete! Copied {images_copied} images.'))
