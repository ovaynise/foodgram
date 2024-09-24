from django.urls import include, path
from rest_framework.routers import DefaultRouter




router = DefaultRouter()


app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
]
