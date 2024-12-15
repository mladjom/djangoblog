from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from blog.models.article_model import Article
from blog.admin.tag_admin import TagInline
from blog.utils.openai_utils import generate_article
from django.utils.html import format_html

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'is_featured', 'created_at', 'updated_at', 'featured_image_thumbnail')
    list_filter = ('is_published', 'is_featured', 'category')  # Filters for sidebar
    search_fields = ('title', 'content')  # Searchable by 'title' and 'content'
    prepopulated_fields = {'slug': ('title',)}  # Auto-generate slug from 'title'
    inlines = [TagInline]  # Add tags inline editing
    date_hierarchy = 'created_at'  # Navigation by creation date
    readonly_fields = ('featured_image_thumbnail', 'created_at', 'updated_at')  # For image preview in the form
    ordering = ('-created_at',)

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content', 'category')
        }),
        ('SEO Metadata', {
            'fields': ('meta_description',),
            'classes': ('collapse',)  
        }),
        ('Publication Status', {
            'fields': ('is_published', 'is_featured')
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

    actions = ['generate_article_content']
    
    def generate_article_content(self, request, queryset):
        for article in queryset:
            #if not article.content:  # Avoid overwriting existing content
            prompt = f'Write a detailed blog article on the topic: {article.title}'
            article.content = generate_article(prompt)
            article.save()
        self.message_user(request, _('Articles content generated successfully.'))

    generate_article_content.short_description = _('Generate content for selected articles')
