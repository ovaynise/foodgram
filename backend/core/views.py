from io import BytesIO

from django.http import FileResponse
from recipes.models import IngredientRecipe, ShoppingCart
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

pdfmetrics.registerFont(TTFont('Arial',
                               'core/fonts/ArialRegular.ttf'))
from django.db.models import Sum


class DownloadShopCartView(APIView):
    """Функция создает список покупок в текстовый файл."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(
            user=user).values_list('recipe', flat=True)

        ingredients = IngredientRecipe.objects.filter(
            recipe__in=shopping_cart_items
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )

        lines = ['Список ингредиентов:\n']
        for count, ingredient in enumerate(ingredients, 1):
            lines.append(
                f"{count}. {ingredient['ingredient__name']}: "
                f"{ingredient['total_amount']} {ingredient['ingredient__measurement_unit']}\n"
            )

        buffer = BytesIO()
        buffer.write(''.join(lines).encode('utf-8'))
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_cart.txt')
