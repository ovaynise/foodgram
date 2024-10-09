from core.serializers import Base64ImageField
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscriptions, Tag)

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj).exists()
        return False


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецептах."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url if obj.image else None
        return request.build_absolute_uri(image_url) if image_url else None


class SubscribeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(
        many=True,
        source='author.recipes',
        read_only=True)
    recipes_count = serializers.IntegerField(
        source='author.recipes.count',
        read_only=True)

    class Meta:
        model = Subscriptions
        fields = ('user', 'author', 'is_subscribed', 'recipes',
                  'recipes_count')

    def create(self, validated_data):
        return Subscriptions.objects.create(**validated_data)

    def to_representation(self, instance):
        """Отображаем пользователя с полным URL изображения
        в ответе и его рецепты."""
        request = self.context.get('request')
        user = instance.author
        image_url = user.avatar.url if user.avatar else None
        recipes = user.recipes.all()[:3]

        return {
            "email": user.email,
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_subscribed": self.get_is_subscribed(instance),
            "recipes": RecipeShortSerializer(
                recipes,
                many=True,
                context=self.context).data,
            "recipes_count": user.recipes.count(),
            "avatar": request.build_absolute_uri(
                image_url) if image_url else None,
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj.author
            ).exists()
        return False


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        """Отображаем рецепт с полным URL изображения в ответе"""
        request = self.context.get('request')
        image_url = instance.recipe.image.url
        if request is not None:
            image_url = request.build_absolute_uri(image_url)

        return {
            "id": instance.recipe.id,
            "name": instance.recipe.name,
            "image": image_url,
            "cooking_time": instance.recipe.cooking_time
        }


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        """Отображаем рецепт с полным URL изображения в ответе"""
        request = self.context.get('request')
        image_url = instance.recipe.image.url
        if request is not None:
            image_url = request.build_absolute_uri(image_url)

        return {
            "id": instance.recipe.id,
            "name": instance.recipe.name,
            "image": image_url,
            "cooking_time": instance.recipe.cooking_time
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    ingredients = IngredientRecipeGetSerializer(many=True,
                                                source='recipe_with_ingredient'
                                                )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipePostSerializer(
        many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient = get_object_or_404(Ingredient, id=ingredient_id)
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags_data = validated_data.get('tags')
        if tags_data:
            instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        if ingredients_data:
            instance.recipe_with_ingredient.all().delete()
            for ingredient_data in ingredients_data:
                ingredient = get_object_or_404(
                    Ingredient,
                    id=ingredient_data['id'])
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data
