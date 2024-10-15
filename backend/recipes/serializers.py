from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscriptions, Tag)
from core.serializers import Base64ImageField

User = get_user_model()


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


class SubscribeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count',
        read_only=True
    )

    class Meta:
        model = Subscriptions
        fields = ('author', 'recipes', 'recipes_count')

    def to_representation(self, instance):
        """Отображаем пользователя с полным URL изображения и его рецепты."""
        request = self.context.get('request')
        user_data = AuthorSerializer(instance.author,
                                     context=self.context).data
        user = instance.author
        limit = request.query_params.get('recipes_limit', None)
        recipes = user.recipes.all()
        if limit is not None:
            recipes = recipes[:int(limit)]
        return {
            **user_data,
            'recipes': RecipeShortSerializer(
                recipes,
                many=True,
                context=self.context).data,
            'recipes_count': user.recipes.count(),
        }

    def get_recipes(self, obj):
        """Получаем рецепты автора с учетом лимита."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context).data


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
        """Сериализатор для рецепта."""
        return RecipeShortSerializer(instance.recipe,
                                     context=self.context).data


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
        """Сериализатор для рецепта."""
        return RecipeShortSerializer(instance.recipe,
                                     context=self.context).data


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
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class IngredientRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipePostSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              required=True,)
    image = Base64ImageField(required=True, allow_null=True)

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

    def validate(self, attrs):
        ingredients_data = attrs.get('ingredients')
        tags_data = attrs.get('tags')
        if not ingredients_data:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле не может быть пустым.'})
        if not tags_data:
            raise serializers.ValidationError(
                {'tags': 'Это поле не может быть пустым.'})
        ingredient_ids = [ingredient['id'] for ingredient in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться.'})
        tags_ids = [tag for tag in tags_data]
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться.'})
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    {'ingredients': f'Ингредиент с ID {ingredient_id} не '
                                    f'существует.'})
            if amount <= 0:
                raise serializers.ValidationError(
                    {'ingredients': f'Количество для '
                                    f'ингредиента с ID {ingredient_id} '
                                    f'должно быть больше 0.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.get('ingredients')
        tags_data = validated_data.get('tags')
        if tags_data:
            instance.tags.set(tags_data)


        if ingredients_data:
            instance.recipe_with_ingredient.all().delete()
            self.create_ingredients(instance, ingredients_data)

        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def create_ingredients(self, recipe, ingredients_data):
        ingredient_objects = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient,
                                             id=ingredient_data['id']),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredient_objects)

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data
