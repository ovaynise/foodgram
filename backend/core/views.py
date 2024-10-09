from io import BytesIO

from core.constants import (BUFFER_START_POSITION, FONT_SIZE,
                            HORIZONTAL_FONT_POSITION, VERTICAL_FONT_POSITION,
                            VERTICAL_SPACING)
from django.http import FileResponse
from recipes.models import IngredientRecipe, ShoppingCart
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

pdfmetrics.registerFont(TTFont('Arial',
                               'core/fonts/ArialRegular.ttf'))


class DownloadShopCartView(APIView):
    """Функция создает список покупок в PDF файл."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        ingredients = {}

        for item in shopping_cart_items:
            recipe = item.recipe
            for ingredient in recipe.ingredients.all():
                amount = IngredientRecipe.objects.get(
                    recipe=recipe, ingredient=ingredient).amount
                if ingredient.name in ingredients:
                    ingredients[ingredient.name]['amount'] += amount
                else:
                    ingredients[ingredient.name] = {
                        'measurement_unit': ingredient.measurement_unit,
                        'amount': amount
                    }

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont('Arial', FONT_SIZE)
        p.drawString(HORIZONTAL_FONT_POSITION,
                     VERTICAL_FONT_POSITION, "Список ингредиентов:")

        y = VERTICAL_FONT_POSITION - VERTICAL_SPACING
        for name, data in ingredients.items():
            p.drawString(HORIZONTAL_FONT_POSITION, y,
                         f"{name}: {data['amount']} "
                         f"{data['measurement_unit']}")
            y -= VERTICAL_SPACING

        p.showPage()
        p.save()

        buffer.seek(BUFFER_START_POSITION)
        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_cart.pdf')
