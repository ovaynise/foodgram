from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (MAX_RECIPE_NAME, MAX_RECIPE_TEXT,
                        MAX_STR_INGRIDIENT_NAME, MAX_STR_MEASUEREMENT_UNIT,
                        MAX_TAG_LENGTH, MIN_TIME_COOKING)
from .validators import validate_tag
from core.models import BaseModel

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_LENGTH,
        verbose_name='Название тега',
        help_text='Имя тэга'
    )
    slug = models.SlugField(
        max_length=MAX_TAG_LENGTH,
        unique=True,
        validators=[validate_tag],
        verbose_name='Слаг',
        help_text='Уникальный слаг тэга для адреса'
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_STR_INGRIDIENT_NAME,
        verbose_name='Название ингредиента',
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=MAX_STR_MEASUEREMENT_UNIT,
        verbose_name='Ед.изм.',
        help_text='Ед.изм.',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(
        max_length=MAX_RECIPE_NAME,
        verbose_name='Название рецепта',
        help_text='Название рецепта',
        unique=True
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Адрес картинки',
        help_text='Картинка',
        blank=True,
        null=True
    )
    text = models.TextField(
        max_length=MAX_RECIPE_TEXT,
        verbose_name='Описание рецепта',
        help_text='Описание рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги рецепта',
        help_text='Тэги рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиент в рецепте',
        help_text='Ингредиент в рецепте',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Время приготовления в минутах',
        validators=[MinValueValidator(MIN_TIME_COOKING)]
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def favorite_count(self):
        return Favorite.objects.filter(recipe=self).count()


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        help_text='Тэг',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        help_text='Название рецепта',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэги с рецептами'
        verbose_name_plural = 'Тэги с рецептами'

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

    class Meta:
        verbose_name = 'Рецепты с ингредиентами'
        verbose_name_plural = 'Рецепты с ингредиентами'

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
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

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
        verbose_name = 'Карточка покупок'
        verbose_name_plural = 'Карточки покупок'

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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} - {self.author}'
