from rest_framework.serializers import ModelSerializer

from constructor.serializers import BlockTypeSerializer
from sales.models import SubscriptionPlan


class SubscriptionPlanSerializer(ModelSerializer):
    """Сериализатор для тарифных планов"""
    allowed_blocks = BlockTypeSerializer(many=True, read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'description', 'allowed_blocks', 'max_sites']