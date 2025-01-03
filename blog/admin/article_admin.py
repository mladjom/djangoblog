from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from blog.models.article_model import Article
from blog.admin.tag_admin import TagInline
from blog.utils.openai_utils import generate_article
from .mixins_admin import DeleteWithImageMixin

@admin.register(Article)
class ArticleAdmin(DeleteWithImageMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'is_published',
        'is_featured',
        'created_at',
        'updated_at',
        'featured_image_thumbnail'
    )
    list_filter = ('is_published', 'is_featured', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TagInline]
    date_hierarchy = 'created_at'
    readonly_fields = (
        'featured_image_thumbnail',
        'featured_image_preview',
        'image_variants_preview',
        'created_at',
        'updated_at'
    )
    ordering = ('-created_at',)

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content', 'category')
        }),
        (_('SEO Metadata'), {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        (_('Publication Status'), {
            'fields': ('is_published', 'is_featured')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        (_('Featured Image'), {
            'fields': (
                'featured_image',
                'featured_image_preview',
                'image_variants_preview'
            ),
            'description': _(
                'Upload an image that will be automatically processed into multiple sizes '
                'maintaining a 16:10 aspect ratio. Available sizes: 576px, 768px, 992px, '
                '1200px, and 1400px width.'
            )
        }),
    )

    def featured_image_thumbnail(self, obj):
        """Display a small thumbnail in the list view"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 50px; object-fit: cover;" />',
                obj.featured_image.url
            )
        return _('No Image')
    featured_image_thumbnail.short_description = _('Thumbnail')

    def featured_image_preview(self, obj):
        """Display a larger preview of the main image"""
        if obj.featured_image:
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<img src="{}" style="max-width: 400px; height: auto;" />'
                '<p style="color: #666; margin-top: 5px;">Main image: {}</p>'
                '</div>',
                obj.featured_image.url,
                obj.featured_image.name
            )
        return _('No image uploaded')
    featured_image_preview.short_description = _('Main Image Preview')

    def image_variants_preview(self, obj):
        """Display previews of all image variants"""
        if not obj.featured_image:
            return _('No image variants available')

        variants = obj.get_image_variants()
        if not variants:
            return _('Processing image variants...')

        html = ['<div style="margin-top: 20px;"><h3>Image Variants</h3>']
        
        # Create a table for variants
        html.append('<table style="border-collapse: collapse; width: 100%; max-width: 800px;">')
        html.append('<tr style="background: #f5f5f5;">'
                   '<th style="padding: 8px; border: 1px solid #ddd;">Size</th>'
                   '<th style="padding: 8px; border: 1px solid #ddd;">Preview</th>'
                   '<th style="padding: 8px; border: 1px solid #ddd;">Path</th></tr>')

        # Sort variants by width
        for width in sorted(variants.keys()):
            variant = variants[width]
            html.append(
                f'<tr style="border: 1px solid #ddd;">'
                f'<td style="padding: 8px; border: 1px solid #ddd;">{width}px</td>'
                f'<td style="padding: 8px; border: 1px solid #ddd;">'
                f'<img src="{variant["url"]}" style="max-width: 150px; height: auto;" />'
                f'</td>'
                f'<td style="padding: 8px; border: 1px solid #ddd; font-size: 12px;">'
                f'{variant["url"]}</td></tr>'
            )

        html.append('</table></div>')
        
        return format_html(''.join(html))
    image_variants_preview.short_description = _('Image Variants') 




    # actions = ['generate_article_content']
    
    # def generate_article_content(self, request, queryset):
    #     for article in queryset:
    #         #if not article.content:  # Avoid overwriting existing content
    #         prompt = f'Write a detailed blog article on the topic: {article.title}'
    #         article.content = generate_article(prompt)
    #         article.save()
    #     self.message_user(request, _('Articles content generated successfully.'))

    # generate_article_content.short_description = _('Generate content for selected articles')
