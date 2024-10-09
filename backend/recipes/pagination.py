from rest_framework.pagination import PageNumberPagination


class IngredientPagination(PageNumberPagination):
    page_size = 10


class RecipePagination(PageNumberPagination):
    page_size = 6
