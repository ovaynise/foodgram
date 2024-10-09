from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (MAX_RECIPE_NAME, MAX_RECIPE_TEXT,
                        MAX_STR_INGRIDIENT_NAME, MAX_STR_MEASUEREMENT_UNIT,
                        MAX_TAG_LENGTH, MIN_TIME_COOKING)
from .validators import validate_tag

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_LENGTH,
        verbose_name='Название тега',
    )
    slug = models.SlugField(
        max_length=MAX_TAG_LENGTH,
        unique=True,
        validators=[validate_tag],
        verbose_name='Slug'
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_STR_INGRIDIENT_NAME,
        verbose_name='Название ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=MAX_STR_MEASUEREMENT_UNIT,
        verbose_name='Единица измерения',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(
        max_length=MAX_RECIPE_NAME,
        verbose_name='Название рецепта',
        unique=True
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка рецепта',
        blank=True,
        null=True
    )
    text = models.TextField(
        max_length=MAX_RECIPE_TEXT,
        verbose_name='Описание рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(MIN_TIME_COOKING)]
    )

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipe.name} - {self.tag.name}"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_on_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_with_ingredient'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    def __str__(self):
        return f"{self.ingredient} - {self.amount}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Избранное'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Карточка пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Карточка пользователя'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Subscriptions(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed',
        verbose_name='Пользователь'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.author}'
