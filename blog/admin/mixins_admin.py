from django.db.models import Count
from django.utils.translation import gettext_lazy as _
import os

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

class DeleteWithImageMixin:
    """
    Admin mixin to handle deletion of models with associated images.
    """
    def delete_queryset(self, request, queryset):
        """
        Deletes associated images for models before removing them from the database.
        """
        for obj in queryset:
            # Check if the model instance has a `featured_image` field
            if hasattr(obj, 'featured_image') and obj.featured_image:
                image_path = obj.featured_image.path
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)  # Delete the associated file
                        self.message_user(request, f"Deleted featured image for: {obj}")
                    except Exception as e:
                        self.message_user(request, f"Error deleting featured image for {obj}: {e}", level="error")

        # Call the parent method to delete the objects
        super().delete_queryset(request, queryset)