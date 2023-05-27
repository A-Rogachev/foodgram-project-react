# Generated by Django 3.2 on 2023-05-27 17:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0015_delete_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoriterecipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Введите название тега', max_length=200, validators=[django.core.validators.RegexValidator(message='Символы $%^&#:;! запрещены для использования!', regex='[-А-Яа-яA-Za-z0-9\\s]+$')], verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Введите слаг для тега', max_length=200, unique=True, verbose_name='Слаг тега'),
        ),
    ]