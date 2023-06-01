import csv
import json
import os
import sys
from enum import Enum
from typing import Dict

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError

from recipes.models import Ingredient, Tag

DATA_DIRECTORY: str = settings.DEFAULT_DATA_FILE_PATH
os.chdir(DATA_DIRECTORY)

data_for_database = [
    Enum(
        'DataFile',
        [
            ('MODEL', Ingredient),
            ('FILENAME', 'ingredients.json'),
            ('FIELD_NAMES', ('name', 'measurement_unit')),
        ]
    ),
    Enum(
        'DataFile',
        [
            ('MODEL', Tag),
            ('FILENAME', 'default_tags.json'),
            ('FIELD_NAMES', ('name', 'color', 'slug')),
        ]
    )
]


class Command(BaseCommand):
    help = 'Загружает данные из файлов .csv или .json в базу данных.'

    def handle(self, *args, **kwargs):
        for data_file in data_for_database:
            try:
                objects_queue = []
                if data_file.FILENAME.value.endswith('csv'):
                    with open(
                        data_file.FILENAME.value, 'r', encoding='utf-8'
                    ) as file:
                        reader = csv.DictReader(
                            file,
                            delimiter=',',
                            quotechar='"',
                            skipinitialspace=True,
                            fieldnames=data_file.FIELD_NAMES.value,
                        )
                        for row in reader:
                            data_args: Dict[str, str] = dict(**row)
                            objects_queue.append(
                                data_file.MODEL.value(**data_args)
                            )

                elif data_file.FILENAME.value.endswith('json'):
                    with open(data_file.FILENAME.value, 'rb') as json_file:
                        full_data_from_file = json.load(json_file)
                        for record in full_data_from_file:
                            new_obj = data_file.MODEL.value(**record)
                            objects_queue.append(new_obj)

                data_file.MODEL.value.objects.bulk_create(objects_queue)
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Файла {data_file.FILENAME.value} нет в '
                        'рабочем каталоге!\nРабота загрузчика прервана!'
                    )
                )
                sys.exit()
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR(
                        f'Oшибка при работе с файлом '
                        f'{data_file.FILENAME.value}\n'
                        'Работа загрузчика прервана!'
                    )
                )
                sys.exit()
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Данные из файла {data_file.FILENAME.value} '
                        'успешно загружены'
                    )
                )
        self.stdout.write(
            self.style.SUCCESS(
                'Работа загрузчика завершена успешно!'
            )
        )
