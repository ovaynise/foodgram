from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from hashids import Hashids
from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.pagination import RecipePagination, SubscribePagination
from .models import (Favorite, Ingredient, Recipe, ShoppingCart, Subscriptions,
                     Tag)
from utils import SHORT_LINK
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)

User = get_user_model()


class RecipeRedirectView(APIView):
    hashids = Hashids(min_length=4, salt=settings.SALT)

    def get(self, request, short_id):
        decoded_id = self.hashids.decode(short_id)
        if not decoded_id:
            return Response({'detail': 'Invalid short link.'}, status=404)
        recipe_id = decoded_id[0]
        return redirect(f'/recipes/{recipe_id}/')


class BaseRecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_recipe(self, recipe_id):
        """Получение рецепта по ID с обработкой 404 ошибки."""
        return get_object_or_404(Recipe, id=recipe_id)

    def handle_create(self, request, recipe_id):
        """Общая логика для создания записи."""
        recipe = self.get_recipe(recipe_id)
        data = {'recipe': recipe.id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def handle_destroy(self, request, recipe_id, model, user):
        """Общая логика для удаления записи."""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        instance = model.objects.filter(recipe=recipe, user=user).first()
        if instance is None:
            return Response(
                {'detail': 'Рецепт не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.delete()
        return Response({'detail': 'Рецепт удалён'},
                        status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        return self.handle_create(request, recipe_id)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        model = self.get_queryset().model
        return self.handle_destroy(request, recipe_id, model, request.user)


class BaseSubscriptionViewSet(viewsets.ModelViewSet):
    """Базовый класс для работы с подписками."""

    def get_queryset(self):
        return Subscriptions.objects.filter(user=self.request.user)

    def create_subscription(self, user, author):
        if user == author:
            return Response({'detail': 'Нельзя '
                                       'подписаться на самого себя.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription, created = Subscriptions.objects.get_or_create(
            user=user,
            author=author
        )
        if not created:
            return Response({'detail': 'Вы уже подписаны '
                                       'на этого пользователя.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        author_id = kwargs.get('pk')
        author = get_object_or_404(User, id=author_id)
        return self.create_subscription(request.user, author)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeShortLinkView(generics.GenericAPIView):
    hashids = Hashids(min_length=4, salt=settings.SALT)

    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        short_id = self.hashids.encode(recipe.id)
        short_link = SHORT_LINK + short_id
        return Response({'short-link': short_link})

    def generate_short_link(self, recipe_id):
        return self.hashids.encode(recipe_id)


class ShoppingCartViewSet(BaseRecipeViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class FavoriteViewSet(BaseRecipeViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class SubscriptionsViewSet(BaseSubscriptionViewSet):
    serializer_class = SubscribeSerializer
    pagination_class = SubscribePagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = (self.get_serializer(page,
                                          many=True) if
                      page is not None else self.get_serializer(queryset,
                                                                many=True))
        return (self.get_paginated_response(serializer
                                            .data) if
                page is not None else Response(serializer.data))


class SubscribeViewSet(BaseSubscriptionViewSet):
    serializer_class = SubscribeSerializer
    pagination_class = SubscribePagination

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs['pk']
        author = get_object_or_404(User, id=author_id)
        subscription = self.get_queryset().filter(author=author).first()
        if subscription is None:
            return Response({'detail': 'Подписка не найдена.'},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()
        return Response({'detail': 'Подписка удалена'},
                        status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def partial_update(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if recipe.author != request.user:
            return Response(
                {'detail': 'У вас нет прав на обновление этого рецепта.'},
                status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(recipe, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if recipe.author != request.user:
            return Response(
                {'detail': 'У вас нет прав на удаление этого рецепта.'},
                status=status.HTTP_403_FORBIDDEN)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
