from django.views.generic import ListView
from blog.models.category_model import Category

class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category/category_list.html'
    context_object_name = 'category_list'
    paginate_by = 10
