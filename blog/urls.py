# blog/urls.py
from django.urls import path
from .views.category_view import CategoryListView, CategoryDetailView
from .views.tag_view import TagListView, TagDetailView
from .views.article_view import ArticleListView, ArticleDetailView
from .sitemaps import CategorySitemap, TagSitemap, ArticleSitemap
from django.contrib.sitemaps.views import sitemap
from .views.pages_view import home, about, contact

sitemaps = {
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'articles': ArticleSitemap,
}

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('privacy/', contact, name='privacy'),
    path('terms/', contact, name='terms'),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('tags/', TagListView.as_view(), name='tags-list'),
    path('articles/', ArticleListView.as_view(), name='articles-list'),
    path('articles/page-<int:page>/', ArticleListView.as_view(), name='article-list-paginated'),
    path('categories/<slug:slug>/page-<int:page>/', CategoryDetailView.as_view(), name='category-detail-paginated'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('tags/<slug:slug>/', TagDetailView.as_view(), name='tag-detail'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]