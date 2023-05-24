import csv
import os
import sys
from typing import Dict

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError
from django.db.models import Model
from recipes.models import Ingredient


DATA_DIRECTORY: str = settings.DATA_FILE_PATH
os.chdir(DATA_DIRECTORY)

data_for_database: Dict[Model, str] = {
    Ingredient: (
        'ingredients.csv',
        ['name', 'measurement_unit'],
    ),
}


class Command(BaseCommand):
    help = 'Загружает данные из файла csv в базу данных.'

    def handle(self, *args, **kwargs):
        for db_model, datafile_and_fields in data_for_database.items():
            try:
                with open(
                    datafile_and_fields[0], 'r', encoding='utf-8'
                ) as data_file:
                    objects_queue = []
                    reader = csv.DictReader(
                        data_file,
                        delimiter=',',
                        quotechar='"',
                        skipinitialspace=True,
                        fieldnames=datafile_and_fields[1],
                    )
                    for row in reader:
                        data_args: Dict[str, str] = dict(**row)
                        objects_queue.append(db_model(**data_args))
                    print(objects_queue)
                    db_model.objects.bulk_create(objects_queue)

            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Файла {datafile_and_fields[0]} нет в рабочем каталоге!'
                        '\nРабота загрузчика прервана!'
                    )
                )
                sys.exit()
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Oшибка при работе с файлом {datafile_and_fields[0]}'
                        '\nРабота загрузчика прервана!'
                    )
                )
                sys.exit()
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Данные из файла {datafile_and_fields[0]} успешно загружены'
                    )
                )
        self.stdout.write(
            self.style.SUCCESS(
                'Работа загрузчика завершена успешно!'
            )
        )
