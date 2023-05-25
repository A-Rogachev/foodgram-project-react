from django.core.exceptions import ValidationError


def validate_username_not_me(value):
    """Имя 'me' запрещено для пользователя, в независимости от регистра."""
    if value.lower() == 'me':
        raise ValidationError(
            f'Имя {value} запрещено для регистрации!'
        )
