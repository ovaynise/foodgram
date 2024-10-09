from django.urls import include, path, re_path
from recipes.views import (DownloadShopCartView, FavoriteViewSet,
                           IngredientViewSet, RecipeShortLinkView,
                           RecipeViewSet, ShoppingCartViewSet,
                           SubscribeViewSet, SubscriptionsViewSet, TagViewSet)
from rest_framework.routers import DefaultRouter
from users.views import AvatarDetail

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')


app_name = "api"

urlpatterns = [
    path('recipes/download_shopping_cart/',
         DownloadShopCartView.as_view(),
         name='download-shopping-cart'),
    path('', include(router.urls)),
    path('recipes/<int:pk>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='favorite'),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart'),
    path('recipes/<int:id>/get-link/',
         RecipeShortLinkView.as_view(),
         name='get-short-link'),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('users/<int:pk>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('', include('djoser.urls')),
    path('users/me/avatar/',
         AvatarDetail.as_view(),
         name='avatar-update'),
]
