from django.contrib.auth import get_user_model
from django.db import models
from core.models import BaseModel

User = get_user_model()


class Tag(BaseModel):
    title = models.CharField(
        max_length=60,
        verbose_name='Название тега',
        unique=True
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        verbose_name='Slug'
    )

    def __str__(self):
        return self.title


class Ingredient(BaseModel):
    title = models.CharField(
        max_length=60,
        verbose_name='Название ингридиента',
    )
    unit_of_measurement = models.CharField(
        max_length=60,
        verbose_name='Единица измерения',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class Recipe(BaseModel):
    title = models.CharField(
        max_length=128,
        verbose_name='Название рецепта',
        unique=True
    )
    image = models.ImageField(
        upload_to='images/recipe/',
        verbose_name='Картинка рецепта',
        blank=True,
        null=True
    )
    about = models.TextField(
        max_length=1000,
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
    cook_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
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


