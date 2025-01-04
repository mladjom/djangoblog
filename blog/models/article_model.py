from django.db import models
from django.utils.translation import gettext_lazy as _
from .category_model import Category
from .tag_model import Tag
from django.urls import reverse
from .featured_image_model import FeaturedImageModel
from .base_model import BaseModelWithSlug
from django.utils.text import Truncator

class Article(BaseModelWithSlug, FeaturedImageModel):
    title = models.CharField(max_length=255, unique=True, verbose_name=_('Title'))
    content = models.TextField(blank=True, null=True,verbose_name=_('Content'))
    excerpt = models.TextField(blank=True, null=True,verbose_name=_('Excerpt'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, related_name='articles', verbose_name=_('Tags'))
    is_published = models.BooleanField(default=False, verbose_name=_('Is Published'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    source_field = 'title'  # Define the source field for the slug

    def get_absolute_url(self):
        return reverse('article-detail', args=[self.slug])

    def update_search_index(self):
        # Logic to update search index goes here
        pass

    @property
    def seo_meta_description(self):
        """
        Use `meta_description` if defined; otherwise, generate a default description.
        """
        return self.meta_description or f"Read about {self.title} and explore related insights."

    def __str__(self):
        return self.title
