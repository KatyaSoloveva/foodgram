import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/ingredients.csv'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                ingredients = [Ingredient(name=row[0], measurement_unit=row[1])
                               for row in reader]
                Ingredient.objects.bulk_create(
                    ingredients, ignore_conflicts=True
                )
            self.stdout.write(self.style.SUCCESS('Ингредиенты добавлены.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Проблемы с открытием файла.'))
