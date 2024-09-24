from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),  # Djoser эндпоинты
    re_path(r'^auth/', include('djoser.urls.authtoken')),  # Djoser токены
]
