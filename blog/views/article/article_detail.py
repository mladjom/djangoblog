from django.views.generic import DetailView
from blog.models.article_model import Article

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article/article_detail.html'
    context_object_name = 'article'
