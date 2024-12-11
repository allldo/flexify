from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import Serializer, ModelSerializer

from cabinet.models import ActivationCode, Profile
from sales.serializers import SubscriptionPlanSerializer


class ProfileSerializer(ModelSerializer):
    """Сериализатор для профиля пользователя"""
    subscription_plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'subscription_plan', 'subscription_start_date']


class RegisterSerializer(Serializer):
    phone_number = CharField(max_length=15)

    def validate_phone_number(self, value):
        # Проверка на уникальность номера телефона
        if ActivationCode.objects.filter(phone_number=value).exists():
            raise ValidationError("Этот номер уже зарегистрирован.")
        return value


class ActivationCodeSerializer(Serializer):
    phone_number = CharField(max_length=15)
    code = CharField(max_length=4)

    def validate(self, data):
        phone_number = data.get('phone_number')
        code = data.get('code')

        # Проверка, существует ли код для этого телефона
        activation_code = ActivationCode.objects.filter(phone_number=phone_number, expired=False).first()
        if not activation_code:
            raise ValidationError("Код для этого номера не найден.")

        # Проверка кода
        if activation_code.get_code != code:
            raise ValidationError("Неверный код.")

        return data