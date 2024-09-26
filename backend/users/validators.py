import re

from django.core.exceptions import ValidationError

from users.constants import MAX_STRING_LENGTH, OWN_USERNAME


def validate_username(username):
    if username:
        if username == OWN_USERNAME:
            raise ValidationError(f'Username не может быть "{OWN_USERNAME}".')
        regex = r'^[a-zA-Z0-9.@+-]+$'
        if not re.match(regex, username):
            raise ValidationError('Username может содержать только буквы, '
                                  'цифры и следующие символы: . @ + - _')
        if len(username) > MAX_STRING_LENGTH:
            raise ValidationError(f'Username не может быть длиннее '
                                  f'{MAX_STRING_LENGTH} символов.')
