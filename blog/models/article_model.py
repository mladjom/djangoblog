from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .category_model import Category
from .tag_model import Tag
from django.urls import reverse
from .featured_image_model import FeaturedImage
import os

class Article(FeaturedImage):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_('Meta Description'))
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

    def get_slug_source(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
            
        # Check if the image is being replaced or cleared
        if self.pk:
            old_article = Article.objects.get(pk=self.pk)
            if old_article.featured_image and old_article.featured_image != self.featured_image:
                try:
                    os.remove(old_article.featured_image.path)
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
        return self.meta_description or f"Discover posts and articles related to {self.title}. Stay updated on trending topics and insights."

    @property
    def canonical_url(self):
        return f"/articles/{self.slug}/"


    def delete(self, *args, **kwargs):
        """
        Ensure the associated image file is deleted when the article is deleted.
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
        return self.title