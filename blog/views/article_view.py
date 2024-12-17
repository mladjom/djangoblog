from django.views.generic import ListView
from django.views.generic import DetailView
from blog.models.article_model import Article
from django.urls import reverse

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article/article_list.html'
    context_object_name = 'article_list'
    paginate_by = 2
    ordering = ['-created_at'] 
    
    def get_queryset(self):
        # Filter only published articles and order by created_at
        return Article.objects.filter(is_published=True).order_by(*self.ordering)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        # Filter only published articles
        return Article.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['breadcrumbs'] = [
            {'name': 'Home', 'url': reverse('homepage')},
            {'name': article.category.name, 'url': reverse('category-detail', args=[article.category.slug])},
            {'name': article.title, 'url': reverse('article-detail', args=[article.slug])}
        ]
        return context
