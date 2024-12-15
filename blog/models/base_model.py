from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class BaseModelWithSlug(models.Model):
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_('Meta Description'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        abstract = True

    def get_absolute_url(self):
        """
        Override this method in subclasses for proper URL resolution.
        """
        raise NotImplementedError("Subclasses must implement `get_absolute_url`")

    def get_slug_source(self):
        """
        Determine the source field for the slug.
        Subclasses must define a `source_field` property or override this method.
        """
        if hasattr(self, 'source_field'):
            return getattr(self, self.source_field)
        raise NotImplementedError("Subclasses must define `source_field` or override `get_slug_source`.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_slug_source())
        super().save(*args, **kwargs)

    @property
    def seo_meta_description(self):
        """
        Use `meta_description` if defined; otherwise, generate a default description.
        Subclasses can override this property if needed.
        """
        return self.meta_description or f"Explore more about {self.get_slug_source()}."

    @property
    def canonical_url(self):
        """
        Generate a canonical URL based on the model's class name and slug.
        """
        return f"/{self.__class__.__name__.lower()}s/{self.slug}/"
