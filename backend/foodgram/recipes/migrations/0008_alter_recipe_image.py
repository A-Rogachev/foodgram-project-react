# Generated by Django 3.2 on 2023-05-24 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_rename_shoppinglist_shoppingcart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Загрузите изображение рецепта', upload_to='recipes/images/', verbose_name='Изображение для рецепта'),
        ),
    ]
