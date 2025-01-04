# blog/models/tag_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .featured_image_model import FeaturedImageModel
from django.urls import reverse
from .base_model import BaseModelWithSlug
from blog.settings import IMAGE_SETTINGS
from blog.utils.image_utils import calculate_height, process_single_image
import os
from django.conf import settings
from django.utils.text import slugify

class Tag(FeaturedImageModel, BaseModelWithSlug):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    source_field = 'name'  # Define the source field for the slug

    def get_absolute_url(self):
        return reverse('tag-detail', args=[self.slug])

    def __str__(self):
        return self.name

    def process_model_specific_image(self):
        """Custom image processing for Category model"""
        if not self.featured_image:
            return

        target_width = IMAGE_SETTINGS['TAXONOMY']['WIDTH']
        aspect_ratio = IMAGE_SETTINGS['TAXONOMY']['ASPECT_RATIO']
        target_height = calculate_height(target_width, aspect_ratio)

        base_filename = slugify(self.name)
        base_path = os.path.dirname(self.featured_image.path)
        new_filename = f"{base_filename}-{target_width}x{target_height}.webp"
        output_path = os.path.join(base_path, new_filename)

        if process_single_image(
            self.featured_image.path, 
            output_path, 
            target_width, 
            quality=IMAGE_SETTINGS['WEBP_QUALITY'],
            aspect_ratio=aspect_ratio
        ):
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
            
        width = IMAGE_SETTINGS['TAXONOMY']['WIDTH']
        height = calculate_height(width, IMAGE_SETTINGS['TAXONOMY']['ASPECT_RATIO'])
        
        return {
            width: {
                'url': f"{settings.MEDIA_URL}{self.featured_image.name}",
                'path': self.featured_image.path
            }
        }