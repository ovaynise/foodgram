
from django.contrib import admin

from .models import (Tag, Ingredient, Recipe)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'unit_of_measurement',
    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'image',
        'about',
        'cook_time'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)