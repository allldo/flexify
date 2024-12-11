from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from sales.models import SubscriptionPlan
from sales.serializers import SubscriptionPlanSerializer


class SubscriptionPlanViewSet(ReadOnlyModelViewSet):
    """Представление для тарифных планов"""
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer