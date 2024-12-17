from django.views.generic import ListView
from django.views.generic import DetailView
from blog.models.article_model import Article
from django.db.models import Count, Q
from blog.models.tag_model import Tag

class TagListView(ListView):
    model = Tag
    template_name = 'blog/tag/tag_list.html'
    context_object_name = 'tag_list'
    ordering = ['name']

    def get_queryset(self):
        return Tag.objects.annotate(
            article_count=Count('articles', filter=Q(articles__is_published=True))
        ).order_by(*self.ordering)

class TagDetailView(DetailView):
    model = Tag
    template_name = 'blog/tag/tag_detail.html'
    context_object_name = 'tag'
    ordering = ['-created_at'] 

    def get_context_data(self, **kwargs):
        """
        Add related articles to the context data.
        """
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(tags=self.object, is_published=True).order_by(*self.ordering)
        return context  
