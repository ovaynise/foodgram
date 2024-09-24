from core.models import BaseModel
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (MAX_RECIPE_NAME, MAX_RECIPE_TEXT,
                        MAX_STR_INGRIDIENT_NAME, MAX_STR_MEASUEREMENT_UNIT,
                        MAX_TAG_LENGTH, MIN_TIME_COOKING)
from .validators import validate_tag

User = get_user_model()


class Tag(BaseModel):
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
        return self.title


class Ingredient(BaseModel):
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
        return self.title


class Recipe(BaseModel):
    name = models.CharField(
        max_length=MAX_RECIPE_NAME,
        verbose_name='Название рецепта',
        unique=True
    )
    image = models.ImageField(
        upload_to='images/recipe/',
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
        related_name='recipes_with_tag'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes_with_ingredient'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(MIN_TIME_COOKING)]
    )

    def __str__(self):
        return self.title


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipe.title} - {self.tag.title}"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recipe.title} - {self.ingredient.title}"
