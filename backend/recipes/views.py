import os

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from dotenv import find_dotenv, load_dotenv
from hashids import Hashids
from recipes.pagination import RecipePagination
from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (Favorite, Ingredient, Recipe, ShoppingCart, Subscriptions,
                     Tag)
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)

User = get_user_model()
load_dotenv(find_dotenv())
SERVER_HOST = os.getenv("SERVER_DOMEN")
SALT = os.getenv("SALT")


class SubscribeViewSet(viewsets.ModelViewSet):
    """ViewSet для подписки и отписки от пользователя"""
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscriptions.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        author_id = self.kwargs['pk']
        author = get_object_or_404(User, id=author_id)
        user = request.user
        if Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscriptions.objects.create(user=user, author=author)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author_id = self.kwargs['pk']
        author = get_object_or_404(User, id=author_id)
        user = request.user
        subscription = get_object_or_404(
            Subscriptions,
            user=user,
            author=author)
        subscription.delete()

        return Response(
            {'detail': 'Подписка удалена'},
            status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """ViewSet для отображения подписок пользователя."""
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Получаем все подписки текущего пользователя
        return Subscriptions.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DownloadShopCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # file_path = 'path/to/your/file.txt'  # Заменить на путь к файлу
        # response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return Response(
            "Здесь будет выдаваться файл",
            status=status.HTTP_200_OK)


class RecipeShortLinkView(generics.GenericAPIView):
    hashids = Hashids(min_length=4, salt="SALT")

    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        short_id = self.hashids.encode(recipe.id)
        short_link = f"https://{SERVER_HOST}/s/{short_id}"
        return Response({"short-link": short_link})

    def generate_short_link(self, recipe_id):
        return self.hashids.encode(recipe_id)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]

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
        favorite = get_object_or_404(
            ShoppingCart,
            recipe__id=recipe_id,
            user=user)
        favorite.delete()

        return Response({'detail': 'Recipe removed from favorites'},
                        status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

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
        favorite = get_object_or_404(Favorite, recipe__id=recipe_id, user=user)
        favorite.delete()
        return Response({'detail': 'Recipe removed from favorites'},
                        status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
