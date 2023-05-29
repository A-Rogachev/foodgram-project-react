# Generated by Django 3.2 on 2023-05-29 13:12

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_subscription_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(help_text='Введите ваше имя', max_length=150, validators=[users.validators.validate_name], verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(help_text='Введите вашу фамилию', max_length=150, validators=[users.validators.validate_name], verbose_name='Фамилия'),
        ),
    ]
