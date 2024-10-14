import os

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from hashids import Hashids
from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

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


class SubscribeViewSet(viewsets.ModelViewSet):
    """ViewSet для подписки и отписки от пользователя."""
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = SubscribePagination

    def get_queryset(self):
        return Subscriptions.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs['pk']
        author = get_object_or_404(User, id=author_id)
        user = request.user
        if user.id == author.id:
            return Response(
                {'detail': 'Вы не можете подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = Subscriptions.objects.create(user=user, author=author)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs['pk']
        author = get_object_or_404(User, id=author_id)
        user = request.user
        subscription = Subscriptions.objects.filter(user=user,
                                                    author=author).first()
        if subscription is None:
            return Response(
                {'detail': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()

        return Response(
            {'detail': 'Подписка удалена'},
            status=status.HTTP_204_NO_CONTENT
        )


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """ViewSet для отображения подписок пользователя."""
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = SubscribePagination

    def get_queryset(self):
        return Subscriptions.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """POST запрос для подписки с поддержкой recipes_limit."""
        author_id = kwargs.get('pk')
        user = request.user
        author = get_object_or_404(User, id=author_id)

        if user == author:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = Subscriptions.objects.get_or_create(
            user=user,
            author=author
        )
        context = self.get_serializer_context()
        context['request'] = request
        serializer = self.get_serializer(subscription, context=context)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RecipeShortLinkView(generics.GenericAPIView):
    hashids = Hashids(min_length=4, salt=settings.SALT)

    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        short_id = self.hashids.encode(recipe.id)
        short_link = SHORT_LINK + short_id
        return Response({'short-link': short_link})

    def generate_short_link(self, recipe_id):
        return self.hashids.encode(recipe_id)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'recipe': recipe.id
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        user = request.user
        recipe_exists = Recipe.objects.filter(id=recipe_id).exists()
        if not recipe_exists:
            return Response(
                {'detail': 'Рецепт не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        shopping_cart_item = ShoppingCart.objects.filter(recipe__id=recipe_id,
                                                         user=user).first()

        if shopping_cart_item is None:
            return Response(
                {'detail': 'Рецепт не найден в корзине.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item.delete()
        return Response({'detail': 'Рецепт удалён из корзины'},
                        status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        data = {
            'recipe': recipe.id
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['pk']
        user = self.request.user
        recipe_exists = Recipe.objects.filter(id=recipe_id).exists()
        if not recipe_exists:
            return Response(
                {'detail': 'Рецепт не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        favorite = Favorite.objects.filter(recipe__id=recipe_id,
                                           user=user).first()
        if favorite is None:
            return Response(
                {'detail': 'Рецепт не найден в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response({'detail': 'Рецепт удалён из избранного'},
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
