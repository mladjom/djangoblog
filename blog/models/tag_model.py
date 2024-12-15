# blog/models/tag_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .featured_image_model import FeaturedImageModel
from django.urls import reverse
from .base_model import BaseModelWithSlug
import os
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

    def delete(self, *args, **kwargs):
        """
        Ensure the associated image file is deleted when the tag is deleted.
        """
        if self.featured_image and self.featured_image.path:
            try:
                os.remove(self.featured_image.path)
            except FileNotFoundError:
                pass  # File might already be deleted
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
