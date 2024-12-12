from rest_framework.serializers import ModelSerializer

from sales.models import SubscriptionPlan


class SubscriptionPlanSerializer(ModelSerializer):
    """Сериализатор для тарифных планов"""

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description', 'max_sites']