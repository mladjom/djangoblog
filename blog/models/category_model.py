import os
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.conf import settings
from blog.utils.image_utils import resize_and_compress_image
from django.urls import reverse
import os
from .featured_image_model import FeaturedImage

class Category(FeaturedImage):
    name = models.CharField( max_length=255, unique=True, verbose_name=_('Name') )
    description = models.TextField( blank=True, null=True, verbose_name=_('Description') )
    slug = models.SlugField( max_length=255, unique=True, verbose_name=_('Slug'), )
    meta_description = models.TextField(blank=True, null=True, verbose_name=_('Meta Description'))
    created_at = models.DateTimeField( _('Created At'), auto_now_add=True )
    updated_at = models.DateTimeField( _('Updated At'), auto_now=True )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    # Add the `get_absolute_url` method
    def get_absolute_url(self):
        return reverse('category-detail', args=[self.slug])

    def get_slug_source(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
            
        # Check if the image is being replaced or cleared
        if self.pk:
            old_category = Category.objects.get(pk=self.pk)
            if old_category.featured_image and old_category.featured_image != self.featured_image:
                try:
                    os.remove(old_category.featured_image.path)
                except FileNotFoundError:
                    pass  # If the file doesn't exist, just skip it           
            
            
        super().save(*args, **kwargs)

        # Process the featured image after the initial save
        if self.featured_image:
            self.process_featured_image()

            # Save again to persist the updated `featured_image` path
            super().save(update_fields=['featured_image'])

    @property
    def seo_meta_description(self):
        return self.meta_description or f"Discover posts and articles related to {self.name}. Stay updated on trending topics and insights."

    @property
    def canonical_url(self):
        return f"/categories/{self.slug}/"


    def delete(self, *args, **kwargs):
        """
        Ensure the associated image file is deleted when the category is deleted.
        """
        if self.featured_image:
            image_path = self.featured_image.path

            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Deleted image: {image_path}")
                except Exception as e:
                    print(f"Error deleting image {image_path}: {e}")
            else:
                print(f"Image file not found: {image_path}")

        super().delete(*args, **kwargs)
            
    def __str__(self):
        return self.name
