from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from blog.models.tag_model import Tag
from blog.models.article_model import Article
from .mixins_admin import ArticleCountMixin
from django.utils.html import format_html

@admin.register(Tag)
class TagAdmin( ArticleCountMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at', 'article_count', 'featured_image_thumbnail')  # Fields displayed in list view
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}  # Auto-generate slug from 'name'
    readonly_fields = ('featured_image_thumbnail', 'created_at', 'updated_at')  # For image preview in the form
       
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description')
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)  # Makes the section collapsible
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Featured Image'), {
            'fields': ('featured_image', 'featured_image_thumbnail'),
            'description': _('Upload an image with a maximum size of 800x800 pixels. The image will be resized and compressed automatically.')
        }),
    )
    
    
    def featured_image_thumbnail(self, obj):
        """Display a thumbnail of the featured image in the admin interface."""
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 80px; height: 80px; object-fit: cover;" />', obj.featured_image.url)
        return _('No Image')

    featured_image_thumbnail.short_description = _('Thumbnail')

    
class TagInline(admin.TabularInline):
    model = Article.tags.through  # Inline Many-to-Many relation for tags
    extra = 1  # Number of empty fields for adding new tags