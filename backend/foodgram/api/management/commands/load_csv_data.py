import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient, Tag


User = get_user_model()


class Command(BaseCommand):
    """Загрузка файлов из CSV файлов."""

    DATA_PATH = 'api/data/'
    CSV_ENCODING = 'utf-8'

    help = 'Load data from CSV files into database'

    def handle(self, *args, **options):
        """Основной метод обработки команды."""
        loaders = {
            'ingredients.csv': (Ingredient, self.load_ingredients),
            'tags.csv': (Tag, self.load_data),
        }

        for filename, (model, func) in loaders.items():
            if model:
                func(filename, model)
            else:
                func(filename)

        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))

    def load_data(self, filename, model):
        """Общая функция загрузки моделей."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as csvfile:

            reader = csv.DictReader(csvfile)
            for row in reader:
                data = {**row}
                try:
                    model.objects.get_or_create(**data)
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f'Объект уже существует: {model.__name__} {data}'
                    ))

    def load_ingredients(self, filename, model):
        """Загрузка модели ингредиентов."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) != 2:
                    continue
                try:
                    model.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(
                        f'Объект уже существует: {model.__name__} '
                        f'{row[0]} {row[1]}'
                    ))
