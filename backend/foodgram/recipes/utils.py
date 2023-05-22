import base64
from rest_framework import serializers
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    """
    Поле для изображений рецептов, закодированных в Base64.
    """

    def _to_internal_value(self, image_data):
        if not isinstance(image_data, str) or image_data.startswith('data:image'):
            raise serializers.ValidationError(
                f'Некорректный формат изображения ({type(image_data).__name__})'
            )
        else:
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1] 
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            return super().to_internal_value(data)
