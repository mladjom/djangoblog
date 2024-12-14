from django.contrib.sitemaps import Sitemap
from blog.models.category_model import Category
from blog.models.tag_model import Tag
from blog.models.article_model import Article

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

class TagSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Article.objects.filter(is_published=True)  # Only include published articles

    def lastmod(self, obj):
        return obj.updated_at