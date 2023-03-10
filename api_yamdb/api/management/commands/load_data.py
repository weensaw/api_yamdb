import csv

from django.conf import settings
from django.core.management import BaseCommand

from ....titles.models import (Category, Comment, GenreTitle, Genre, Review,
                    Title, User)

CSV_LIST_DICT = {
    Category: 'category.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv',
    Genre: 'genre.csv',
    Review: 'review.csv',
    Title: 'titles.csv',
    User: 'users.csv'
}


class Command(BaseCommand):
    help = 'Выгружаем данные из csv-файлов.'

    def handle(self, *args, **kwargs):
        for model, file in CSV_LIST_DICT.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{file}', 'r',
                encoding='utf-8'
            ) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        model.objects.create(**row)
                    except Exception as e:
                        print(f'Ошибочка вышла: {e}.')
            