from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from sales.models import SubscriptionPlan


class SubscriptionPlanSerializer(ModelSerializer):
    """Сериализатор для тарифных планов"""
    duration_text = SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description', 'period',
                  'duration_days', 'is_trial', 'max_sites', 'duration_text']

    def get_duration_text(self, obj):
        """Возвращает текстовое описание длительности подписки"""
        if obj.period == 'trial':
            return f"Пробный период на {obj.duration_days} дней"
        elif obj.period == 'monthly':
            return "Месячная подписка"
        elif obj.period == 'yearly':
            return "Годовая подписка"
        return f"{obj.duration_days} дней"