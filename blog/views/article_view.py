from django.views.generic import ListView
from django.views.generic import DetailView
from blog.models.article_model import Article

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article/article_list.html'
    context_object_name = 'article_list'
    paginate_by = 10
    
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article/article_detail.html'
    context_object_name = 'article'


