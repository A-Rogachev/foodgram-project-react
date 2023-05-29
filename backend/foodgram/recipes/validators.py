import re

from django.core.exceptions import ValidationError


def validate_for_nonpunctuation_marks(value):
    """
    Проверка строки на остуствие знаков препинания.
    """
    if re.fullmatch(
        pattern=r'[-А-Яа-яA-Za-z0-9\s]+$',
        string=value,
    ) is None:
        raise ValidationError(
            'Символы $%^&#:;! запрещены для использования!'
        )
