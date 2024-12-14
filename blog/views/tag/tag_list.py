from django.views.generic import ListView
from blog.models.tag_model import Tag

class TagListView(ListView):
    model = Tag
    template_name = 'blog/tag/tag_list.html'
    context_object_name = 'tag_list'
    paginate_by = 10
