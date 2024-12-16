from django.views.generic import ListView
from django.views.generic import DetailView
from blog.models.category_model import Category
from blog.models.article_model import Article

class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category/category_list.html'
    context_object_name = 'category_list'
    ordering = ['name']

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(category=self.object, is_published=True).order_by('-created_at')
        return context    