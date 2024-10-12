from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class IngredientPagination(PageNumberPagination):
    page_size = 10


class RecipePagination(PageNumberPagination):
    page_size = 6


class SubscribePagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10
