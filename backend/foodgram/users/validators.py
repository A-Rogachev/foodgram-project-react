import re

from django.core.exceptions import ValidationError


def validate_username_not_me(value):
    """
    Имя 'me' запрещено для пользователя, в независимости от регистра.
    """
    if value.lower() == 'me':
        raise ValidationError(
            f'Имя {value} запрещено для регистрации!'
        )


def validate_name(value):
    """
    Проверка строки на недопустимые символы.
    """
    if re.fullmatch(
        pattern=r'[А-Яа-яA-Za-z]+$',
        string=value,
    ) is None:
        raise ValidationError(
            'Вводимое значение должно содержать только буквы!'
        )
