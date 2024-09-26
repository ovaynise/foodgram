from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import AvatarDetail

router = DefaultRouter()


app_name = "api"

urlpatterns = [
    path('', include('djoser.urls')),  # Djoser эндпоинты
    re_path(r'^auth/', include('djoser.urls.authtoken')),  # Djoser токены
    path('users/me/avatar/', AvatarDetail.as_view(), name='avatar-update'),
]
