from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from blog.models.article_model import Article
from blog.admin.tag_admin import TagInline
from blog.utils.openai_utils import generate_article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('is_published', 'is_featured', 'category')  # Filters for sidebar
    search_fields = ('title', 'content')  # Searchable by 'title' and 'content'
    prepopulated_fields = {'slug': ('title',)}  # Auto-generate slug from 'title'
    inlines = [TagInline]  # Add tags inline editing
    date_hierarchy = 'created_at'  # Navigation by creation date
    readonly_fields = ('created_at', 'updated_at')  # Prevent manual changes to timestamps
    
    actions = ['generate_article_content']
    
    def generate_article_content(self, request, queryset):
        for article in queryset:
            #if not article.content:  # Avoid overwriting existing content
            prompt = f'Write a detailed blog article on the topic: {article.title}'
            article.content = generate_article(prompt)
            article.save()
        self.message_user(request, _('Articles content generated successfully.'))

    generate_article_content.short_description = _('Generate content for selected articles')
