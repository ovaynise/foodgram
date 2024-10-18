from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


from recipes.views import RecipeRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('s/<str:short_id>/', RecipeRedirectView.as_view(),
         name='recipe-redirect'),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
