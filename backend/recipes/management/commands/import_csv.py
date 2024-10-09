import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient

User = get_user_model()

FILES = {
    'ingredients.csv': Ingredient,
    # Добавьте другие модели и их соответствующие CSV-файлы
}


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов'

    def handle(self, *args, **kwargs):
        for csv_file, model in FILES.items():
            try:
                file_path = os.path.join(settings.CSV_DATA_PATH, csv_file)
                with open(file_path, encoding='utf-8') as file:
                    reader = csv.DictReader(file)  # Читаем CSV с заголовками
                    for row in reader:
                        # Убедитесь, что в строке есть все необходимые поля
                        if 'name' in row and 'measurement_unit' in row:
                            # Создаем или обновляем объект модели
                            obj, created = model.objects.update_or_create(
                                name=row['name'],  # Используем поле name
                                measurement_unit=row['measurement_unit']
                                # Используем поле measurement_unit
                            )

                            if created:
                                self.stdout.write(
                                    f'Создан новый '
                                    f'объект {model.__name__}: {obj}')
                            else:
                                self.stdout.write(
                                    f'Обновлён объект {model.__name__}: {obj}')

            except FileNotFoundError as error:
                raise CommandError(f'Файл не найден: {error}')
            except Exception as e:
                raise CommandError(
                    f'Ошибка при импорте данных из {csv_file}: {e}')

        self.stdout.write('Импорт данных завершён')
