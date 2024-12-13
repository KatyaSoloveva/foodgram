import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, measurement_unit = row
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit)
        self.stdout.write(self.style.SUCCESS('Ингредиенты добавлены.'))
