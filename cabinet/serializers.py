from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.serializers import Serializer, ModelSerializer

from cabinet.models import ActivationCode, Profile, CustomUser
from sales.serializers import SubscriptionPlanSerializer


class ProfileSerializer(ModelSerializer):
    """Сериализатор для профиля пользователя"""
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    subscription_status = SerializerMethodField()
    days_left = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'subscription_plan', 'subscription_start_date',
                  'subscription_end_date', 'is_active', 'subscription_status', 'days_left']

    def get_subscription_status(self, obj):
        """Возвращает текстовый статус подписки"""
        if not obj.subscription_plan:
            return "Нет активной подписки"

        if obj.is_subscription_expired:
            return "Подписка истекла"

        if obj.subscription_plan.is_trial:
            return "Пробный период"

        return "Активна"

    def get_days_left(self, obj):
        """Возвращает количество дней до окончания подписки"""
        if not obj.subscription_end_date:
            return 0

        from django.utils import timezone
        today = timezone.now().date()
        if obj.subscription_end_date < today:
            return 0

        delta = obj.subscription_end_date - today
        return delta.days


class RegisterSerializer(Serializer):
    email = CharField(max_length=255)
    password = CharField(min_length=6, max_length=128)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return value


class LoginSerializer(Serializer):
    email = CharField(max_length=255)
    password = CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            if not user.check_password(password):
                raise ValidationError("Неверный email или пароль.")
        except CustomUser.DoesNotExist:
            raise ValidationError("Неверный email или пароль.")

        return data


class ActivationCodeSerializer(Serializer):
    email = CharField(max_length=255)
    code = CharField(max_length=4)
    password = CharField(min_length=4, max_length=128)

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        password = data.get('password')
        activation_code = ActivationCode.objects.filter(email=email, code=code, expired=False)
        if not activation_code:
            raise ValidationError("Код для этого email не найден.")

        # Проверка кода
        if activation_code.code != code:
            raise ValidationError("Неверный код.")

        CustomUser.objects.create_user(email=email, password=password)

        return data