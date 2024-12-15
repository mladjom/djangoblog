from django.views.generic import ListView
from django.views.generic import DetailView
from blog.models.article_model import Article

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


