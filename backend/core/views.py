from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from recipes.models import IngredientRecipe

pdfmetrics.registerFont(TTFont('Arial',
                               'core/fonts/ArialRegular.ttf'))


class DownloadShopCartView(APIView):
    """Создает список покупок в текстовый файл."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        ingredients = (IngredientRecipe.objects
                       .filter(recipe__shoppingcart__user=user)
                       .values('ingredient__name', 'ingredient__measurement_unit')
                       .annotate(total_amount=Sum('amount'))
                       .order_by('ingredient__name'))
        lines = ['Список ингредиентов:\n']
        for ingredient in ingredients:
            lines.append(
                f'{ingredient["ingredient__name"]}: '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )

        buffer = BytesIO()
        buffer.write(''.join(lines).encode('utf-8'))
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_cart.txt')
