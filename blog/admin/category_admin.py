# blog/admin/category_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from blog.models.category_model import Category
from .mixins_admin import ArticleCountMixin
import os

@admin.register(Category)
class CategoryAdmin(ArticleCountMixin, admin.ModelAdmin):
    list_display = ('name', 'id','slug', 'created_at', 'updated_at', 'article_count', 'featured_image_thumbnail')  # Fields displayed in list view
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}  # Auto-generate slug from 'name'
    readonly_fields = ('featured_image_thumbnail',)  # For image preview in the form
       
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description')
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
    
    
    def delete_queryset(self, request, queryset):
        """
        Overriding delete_queryset to remove associated images for selected categories.
        """
        for category in queryset:
            if category.featured_image:
                image_path = category.featured_image.path
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)  # Delete the image file
                    except Exception as e:
                        self.message_user(request, f"Error deleting image for {category.name}: {e}", level="error")
        # Call the default delete action
        queryset.delete()