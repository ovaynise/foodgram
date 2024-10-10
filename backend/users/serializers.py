from core.serializers import Base64ImageField
from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import TokenCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import Subscriptions
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from backend.settings import LOGIN_FIELD

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar', None)
        if avatar:
            instance.avatar = avatar
        instance.save()
        return instance


class CustomUserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar', 'password'
        )

    def validate(self, attrs):
        if 'first_name' not in attrs or not attrs['first_name']:
            raise serializers.ValidationError(
                {"first_name": "Это поле обязательно."})
        if 'last_name' not in attrs or not attrs['last_name']:
            raise serializers.ValidationError(
                {"last_name": "Это поле обязательно."})
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if password is None:
            raise serializers.ValidationError("Пароль обязателен.")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscriptions.objects.filter(user=request.user,
                                                author=obj).exists()
        return False

    def to_representation(self, instance):
        request = self.context.get('request')
        if request.path == '/api/users/me/' and request.user.is_anonymous:
            raise AuthenticationFailed("Пожалуйста, авторизуйтесь.")
        if request.method == 'POST':
            return {
                "email": instance.email,
                "id": instance.id,
                "username": instance.username,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
            }

        return super().to_representation(instance)


class CustomTokenCreateSerializer(TokenCreateSerializer):
    """Сериализатор создания и выдачи токена по email."""
    password = serializers.CharField(
        required=False,
        style={"input_type": "password"})

    default_error_messages = {
        "invalid_credentials": "Не правильный Email или Password",
        "inactive_account": "Нет аккаунтов с такими данными",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields[LOGIN_FIELD] = serializers.CharField(required=False)

    def validate(self, attrs):
        password = attrs.get("password")
        params = {LOGIN_FIELD: attrs.get(LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")
