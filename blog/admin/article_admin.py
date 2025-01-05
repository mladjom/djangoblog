from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from blog.models.article_model import Article
from blog.admin.tag_admin import TagInline
from blog.utils.openai_utils import generate_article
from .mixins_admin import DeleteWithImageMixin
import os
import logging
from blog.models.category_model import Category
from blog.models.tag_model import Tag
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
import json
from django.views.decorators.csrf import ensure_csrf_cookie

logger = logging.getLogger(__name__)

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
    filter_horizontal = ['tags']  # Better UI for managing tags
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TagInline]
    date_hierarchy = 'created_at'
    readonly_fields = (
        'featured_image_thumbnail',
        'featured_image_preview',
        'image_variants_preview',
        'created_at',
        'updated_at',
        'suggestion_area',
    )
    ordering = ('-created_at',)

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug','content', 'excerpt', 'category')
        }),
        (_('SEO Metadata'), {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        (_('Content Suggestions'), {
            'fields': ('suggestion_area',),
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
        """Display previews of all image variants."""
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

        for width, variant in sorted(variants.items()):
            try:
                # Ensure the variant file exists
                if os.path.exists(variant['path']):
                    html.append(
                        f'<tr>'
                        f'<td style="padding: 8px; border: 1px solid #ddd;">{width}px</td>'
                        f'<td style="padding: 8px; border: 1px solid #ddd;">'
                        f'<img src="{variant["url"]}" style="max-width: 150px; height: auto;" />'
                        f'</td>'
                        f'<td style="padding: 8px; border: 1px solid #ddd; font-size: 12px;">'
                        f'{variant["url"]}</td></tr>'
                    )
                else:
                    html.append(
                        f'<tr>'
                        f'<td style="padding: 8px; border: 1px solid #ddd;">{width}px</td>'
                        f'<td style="padding: 8px; border: 1px solid #ddd; color: red;">File missing</td>'
                        f'<td style="padding: 8px; border: 1px solid #ddd; font-size: 12px;">'
                        f'{variant["url"]}</td></tr>'
                    )
            except Exception as e:
                logger.error(f"Error loading variant {variant['path']}: {e}")
                html.append(
                    f'<tr>'
                    f'<td style="padding: 8px; border: 1px solid #ddd;">{width}px</td>'
                    f'<td colspan="2" style="padding: 8px; border: 1px solid #ddd; color: red;">Error loading variant</td>'
                    f'</tr>'
                )

        html.append('</table></div>')

        return format_html(''.join(html))

    def get_urls(self):
        """Add custom URLs for AJAX endpoints"""
        urls = super().get_urls()
        custom_urls = [
            path('suggest/<int:article_id>/',
                 self.admin_site.admin_view(self.get_suggestions),
                 name='article-suggestions'),
            path('create-tag/',
                self.admin_site.admin_view(ensure_csrf_cookie(self.create_tag)),
                 name='create-tag'),
            path('create-category/',
                 self.admin_site.admin_view(ensure_csrf_cookie(self.create_category)),
                 name='create-category'),
        ]
        return custom_urls + urls
    
    def suggestion_area(self, obj):
        """Render the suggestion area."""
        if obj.pk:
            context = {'article_id': obj.pk}
            return render_to_string('admin/article_suggestion_area.html', context)
        return "Save the article first to get suggestions"
    suggestion_area.allow_tags = True
    suggestion_area.short_description = "Content Suggestions"
    

    def get_suggestions(self, request, article_id):
        """AJAX endpoint for getting suggestions"""
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
            
        article = get_object_or_404(Article, pk=article_id)
        raw_suggestions = article.suggest_content_tags_and_categories()
        
        # Format suggestions properly
        formatted_suggestions = {
            'tags': [
                {
                    'type': suggestion[0],
                    'info': {
                        'id': suggestion[1].id if suggestion[0] == 'existing' else None,
                        'name': suggestion[1].name if suggestion[0] == 'existing' else suggestion[1]['name']
                    }
                }
                for suggestion in raw_suggestions.get('tags', [])
            ],
            'categories': [
                {
                    'type': suggestion[0],
                    'info': {
                        'id': suggestion[1].id if suggestion[0] == 'existing' else None,
                        'name': suggestion[1].name if suggestion[0] == 'existing' else suggestion[1]['name']
                    }
                }
                for suggestion in raw_suggestions.get('categories', [])
            ]
        }
        
        return JsonResponse(formatted_suggestions)

    def create_tag(self, request):
        """Handle tag creation AJAX request"""
        if not request.user.has_perm('blog.add_tag'):
            raise PermissionDenied
        
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
        try:
            data = json.loads(request.body)
            tag_name = data.get('name')
            
            if not tag_name:
                return JsonResponse({'error': 'Tag name is required'}, status=400)
                
            # Check if tag already exists
            tag = Tag.objects.filter(name__iexact=tag_name).first()
            if tag:
                return JsonResponse({
                    'id': tag.id,
                    'name': tag.name,
                    'message': 'Tag already exists'
                })
            
            # Create new tag
            tag = Tag.objects.create(name=tag_name)
            return JsonResponse({
                'id': tag.id,
                'name': tag.name,
                'message': 'Tag created successfully'
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def create_category(self, request):
        """AJAX endpoint for creating a new category"""
        import json
        data = json.loads(request.body)
        category = Category.objects.create(name=data['name'])
        return JsonResponse({'id': category.id, 'name': category.name})

    class Media:
        css = {
            'all': ('admin/css/article_suggestions.css',)
        }
        js = ('admin/js/article_suggestions.js',)

    # actions = ['generate_article_content']
    
    # def generate_article_content(self, request, queryset):
    #     for article in queryset:
    #         #if not article.content:  # Avoid overwriting existing content
    #         prompt = f'Write a detailed blog article on the topic: {article.title}'
    #         article.content = generate_article(prompt)
    #         article.save()
    #     self.message_user(request, _('Articles content generated successfully.'))

    # generate_article_content.short_description = _('Generate content for selected articles')
