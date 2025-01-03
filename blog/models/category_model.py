# blog/models/category_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .featured_image_model import FeaturedImageModel
from django.urls import reverse
from .base_model import BaseModelWithSlug
from blog.utils.image_utils import calculate_height, process_single_image
from django.utils.text import slugify
import os
from django.conf import settings

class Category(FeaturedImageModel, BaseModelWithSlug):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    source_field = 'name'  # Define the source field for the slug

    def get_absolute_url(self):
        return reverse('category-detail', args=[self.slug])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Define the specific width and aspect ratio for the image size
        target_width = 768  # Example width, adjust as needed
        aspect_ratio = (16, 10)

        # Process the featured image to create only one size variant
        if self.featured_image:
            # Use the process_single_image method to resize and save only the one specific size
            output_path = self.featured_image.path.replace(self.featured_image.name,
                        f'{self.featured_image.name}-{target_width}x{calculate_height(target_width, aspect_ratio)}.webp')

            # Call the process_single_image function to resize and save
            if process_single_image(self.featured_image.path, output_path, target_width, aspect_ratio=aspect_ratio):
                # After processing, update the image field with the new processed image path
                self.featured_image.name = output_path

        # Save the category instance after processing the image
        super().save(*args, **kwargs)

    def process_model_specific_image(self):
        """Custom image processing for Category model"""
        if not self.featured_image:
            return

        target_width = 768
        aspect_ratio = (16, 10)
        target_height = calculate_height(target_width, aspect_ratio)

        # Create base filename from category name
        base_filename = slugify(self.name)
        base_path = os.path.dirname(self.featured_image.path)
        
        # Create new filename
        new_filename = f"{base_filename}-{target_width}x{target_height}.webp"
        output_path = os.path.join(base_path, new_filename)

        # Process the image
        if process_single_image(self.featured_image.path, output_path, target_width, aspect_ratio=aspect_ratio):
            # Delete original if different
            if self.featured_image.path != output_path and os.path.exists(self.featured_image.path):
                os.remove(self.featured_image.path)
            
            # Update the image field with relative path
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            self.featured_image.name = relative_path

    def get_image_variants(self):
        """Override to return only single size variant"""
        if not self.featured_image:
            return {}
            
        width = 768
        height = calculate_height(width)
        base_path = os.path.dirname(self.featured_image.path)
        filename = os.path.basename(self.featured_image.name)
        
        return {
            width: {
                'url': f"{settings.MEDIA_URL}{self.featured_image.name}",
                'path': self.featured_image.path
            }
        }