from django.contrib import admin

from .models import (Ingredient, Recipe, Tag, TagRecipe, IngredientRecipe,
                     Favorite, ShoppingCart, Subscriptions)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    empty_value_display = 'Не задано'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = 'Не задано'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'image',
        'text',
        'cooking_time',
        'author',
        'get_favorite_count'
    )
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)
    empty_value_display = 'Не задано'

    def get_favorite_count(self, obj):
        return obj.favorite_count()

    get_favorite_count.short_description = 'В избранном'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    empty_value_display = 'Не задано'


class TagRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tag',
        'recipe',
    )
    empty_value_display = 'Не задано'


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount',
    )
    empty_value_display = 'Не задано'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    empty_value_display = 'Не задано'


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'user',
    )
    empty_value_display = 'Не задано'


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(TagRecipe, TagRecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
