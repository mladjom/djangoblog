from django.views.generic import DetailView
from blog.models.category_model import Category

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category/category_detail.html'
    context_object_name = 'category'
