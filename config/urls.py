# main/urls.py
from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('', include('blog.urls')),  # Include blog URLs here
    path("__reload__/", include("django_browser_reload.urls")),
]

# Add admin URLs with language prefix
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)

# Debug-specific URLs
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    # Serve static files during development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
