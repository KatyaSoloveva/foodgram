import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/tags.csv'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                tags = [Tag(name=row[0], slug=row[1]) for row in reader]
                Tag.objects.bulk_create(
                    tags, ignore_conflicts=True
                )
            self.stdout.write(self.style.SUCCESS('Теги добавлены.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Проблемы с открытием файла.'))
