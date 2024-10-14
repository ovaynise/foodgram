import re

from django.core.exceptions import ValidationError

from recipes.constants import MAX_TAG_LENGTH


def validate_tag(name):
    if name:
        regex = r'^[-a-zA-Z0-9_]+$'
        if not re.match(regex, name):
            raise ValidationError('name может содержать только буквы, ')
        if len(name) > MAX_TAG_LENGTH:
            raise ValidationError(f'name не может быть длиннее '
                                  f'{MAX_TAG_LENGTH} символов.')
