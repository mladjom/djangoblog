from django.views.generic import DetailView
from blog.models.tag_model import Tag

class TagDetailView(DetailView):
    model = Tag
    template_name = 'blog/tag/tag_detail.html'
    context_object_name = 'tag'
