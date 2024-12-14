from django.db.models import Count
from django.utils.translation import gettext_lazy as _

class ArticleCountMixin:
    # Custom method to count related articles optimized with Annotations
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(article_count=Count('articles'))

    # Use the annotated field for display
    def article_count(self, obj):
        return obj.article_count
    
    #     # Makes the column sortable
    article_count.admin_order_field = 'article_count'
    
    # # Add a short description for the admin column
    article_count.short_description = _('Articles')