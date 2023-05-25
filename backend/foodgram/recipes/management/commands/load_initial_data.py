import csv
import json
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
                objects_queue = []
                if datafile_and_fields[0].endswith('csv'):
                    with open(
                        datafile_and_fields[0], 'r', encoding='utf-8'
                    ) as data_file:
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

                elif datafile_and_fields[0].endswith('json'):
                    with open(datafile_and_fields[0], 'rb') as json_file:
                        full_data_from_file = json.load(json_file)
                        for record in full_data_from_file:
                            new_obj = db_model(**record)
                            objects_queue.append(new_obj)

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
