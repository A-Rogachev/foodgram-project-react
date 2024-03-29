# Generated by Django 3.2 on 2023-05-29 14:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0022_auto_20230529_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientamount',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, help_text='Выберите количество ингредиента', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(2000)], verbose_name='Количество'),
        ),
    ]
