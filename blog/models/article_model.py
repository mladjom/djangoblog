from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .category_model import Category
from .tag_model import Tag
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, related_name='articles', verbose_name=_('Tags'))
    is_published = models.BooleanField(default=False, verbose_name=_('Is Published'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    # Add the `get_absolute_url` method
    def get_absolute_url(self):
        return reverse('article-detail', args=[self.slug])


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title