# blog/models/category_model.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from .featured_image_model import FeaturedImageModel
from django.urls import reverse
from .base_model import BaseModelWithSlug

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