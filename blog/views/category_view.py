from django.views.generic import ListView
from django.views.generic import DetailView
from blog.models.category_model import Category
from blog.models.article_model import Article
from django.db.models import Count, Q

class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category/category_list.html'
    context_object_name = 'category_list'
    ordering = ['name']

    def get_queryset(self):
        # Annotate categories with the number of related articles
        return Category.objects.annotate(
            article_count=Count('articles', filter=Q(articles__is_published=True))
            ).order_by(*self.ordering)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category/category_detail.html'
    context_object_name = 'category'
    paginate_by = 1
    ordering = ['-created_at'] 

    def get_context_data(self, **kwargs):
        """
        Add related articles to the context data.
        """
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(category=self.object, is_published=True).order_by(*self.ordering)
        return context  
