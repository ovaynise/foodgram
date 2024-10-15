from django.contrib.auth import get_user_model
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import FilterSet, filters
from django.db.models import Count, F, Subquery

from .models import Ingredient, Recipe, Subscriptions, Tag

User = get_user_model()


class SubscriptionsFilter(django_filters.FilterSet):
    recipes_limit = filters.NumberFilter(method='filter_recipes_limit')

    class Meta:
        model = Subscriptions
        fields = ['recipes_limit']

    def filter_recipes_limit(self, queryset, name, value):
        if value is not None:
            recipe_ids = (Recipe.objects
                          .filter(author=F('author'))
                          .values('id')[:value])
            queryset = queryset.annotate(
                recipes_count=Count('author__recipe'),
                recipes=Subquery(recipe_ids)
            )
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=self.request.user)
            else:
                return queryset.exclude(shopping_cart__user=self.request.user)
        return queryset
