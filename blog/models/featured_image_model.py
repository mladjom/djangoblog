import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import logging
from blog.utils.image_utils import (
    resize_and_compress_images,
    image_upload_path,
    calculate_height,
    process_single_image
)

logger = logging.getLogger(__name__)

class FeaturedImageModel(models.Model):
    featured_image = models.ImageField(
        upload_to=image_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Featured Image")
    )

    class Meta:
        abstract = True

    @property
    def image_sizes(self):
        """Define the required image sizes"""
        return [576, 768, 992, 1200, 1400]



    def get_image_variants(self):
        """Get all image variants paths"""
        if not self.featured_image:
            return {}
        
        variants = {}
        base_path = os.path.dirname(self.featured_image.path)
        original_name = os.path.basename(self.featured_image.name)
        # Keep the full filename except dimensions and extension
        base_name = '-'.join(original_name.split('-')[:-1]) if '-' in original_name else original_name.split('.')[0]
        
        for width in self.image_sizes:
            height = calculate_height(width)
            filename = f"{base_name}-{width}x{height}.webp"
            relative_path = os.path.join(os.path.dirname(self.featured_image.name), filename)
            variants[width] = {
                'url': f"{settings.MEDIA_URL}{relative_path}",
                'path': os.path.join(base_path, filename)
            }
        return variants

    def handle_old_featured_image(self):
        """Handle deletion of old featured image and its variants"""
        if self.pk:
            try:
                old_instance = type(self).objects.get(pk=self.pk)
                if old_instance.featured_image and old_instance.featured_image != self.featured_image:
                    # Remove main image
                    try:
                        if os.path.exists(old_instance.featured_image.path):
                            os.remove(old_instance.featured_image.path)
                    except Exception as e:
                        logger.error(f"Error removing original image: {e}")

                    # Remove all variants
                    for variant in old_instance.get_image_variants().values():
                        try:
                            if os.path.exists(variant['path']):
                                os.remove(variant['path'])
                        except Exception as e:
                            logger.error(f"Error removing variant: {e}")
            except type(self).DoesNotExist:
                pass


    # def create_thumbnail(self, width=576):
        """Create a thumbnail from the featured image"""
        if not self.featured_image:
            return None

        try:
            base_path = os.path.dirname(self.featured_image.path)
            slug_source = getattr(self, 'name', None) or getattr(self, 'title', None) or 'default'
            base_filename = slugify(slug_source)
            
            height = calculate_height(width)
            thumbnail_filename = f"{base_filename}-{width}x{height}.webp"
            thumbnail_path = os.path.join(base_path, thumbnail_filename)
            
            success = process_single_image(
                image_path=self.featured_image.path,
                output_path=thumbnail_path,
                target_width=width,
                quality=85,
                aspect_ratio=(16, 10)
            )
            
            if success:
                return {
                    'url': f"{settings.MEDIA_URL}{os.path.relpath(thumbnail_path, settings.MEDIA_ROOT)}",
                    'path': thumbnail_path
                }
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
        
        return None


    def process_featured_image(self):
        """Process the featured image and create all required sizes"""
        if not self.featured_image:
            return

        # Allow model-specific image processing
        if hasattr(self, 'process_model_specific_image'):
            self.process_model_specific_image()
            return

        # Default multi-size processing
        slug_source = getattr(self, 'name', None) or getattr(self, 'title', None) or 'default'
        base_filename = slugify(slug_source)
        
        original_path = self.featured_image.path
        base_path = os.path.dirname(original_path)
        
        results = resize_and_compress_images(
            image_path=original_path,
            base_path=base_path,
            new_base_filename=base_filename,  # Pass the slugified title as the new base filename
            sizes=self.image_sizes,
            quality=85,
            aspect_ratio=(16, 10)
        )
        
        if results:
            largest_size = max(self.image_sizes)
            largest_height = calculate_height(largest_size)
            main_filename = f"{base_filename}-{largest_size}x{largest_height}.webp"
            new_main_path = os.path.join(base_path, main_filename)
            
            if original_path != new_main_path and os.path.exists(original_path):
                os.remove(original_path)
            
            # Update the field with relative path
            relative_path = os.path.relpath(new_main_path, settings.MEDIA_ROOT)
            self.featured_image.name = relative_path

    def save(self, *args, **kwargs):
        """Save the model and process images"""
        is_new_instance = self.pk is None
        
        # Handle old image replacement
        if not is_new_instance:
            self.handle_old_featured_image()

        # Save instance first to apply upload_to logic
        super().save(*args, **kwargs)

        # Process the featured image after initial save
        if self.featured_image:
            self.process_featured_image()
            super().save(update_fields=['featured_image'])

    def delete(self, *args, **kwargs):
        """Delete all image variants when the model instance is deleted"""
        if self.featured_image:
            # Delete all image variants
            for variant in self.get_image_variants().values():
                try:
                    if os.path.exists(variant['path']):
                        os.remove(variant['path'])
                except Exception as e:
                    logger.error(f"Error deleting variant: {e}")

            # Delete original image
            try:
                if os.path.exists(self.featured_image.path):
                    os.remove(self.featured_image.path)
            except Exception as e:
                logger.error(f"Error deleting original image: {e}")

        super().delete(*args, **kwargs)
