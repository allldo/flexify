from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from sales.models import SubscriptionPlan
from sales.serializers import SubscriptionPlanSerializer

# sales/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from cabinet.models import Profile
from cabinet.serializers import ProfileSerializer
from sales.models import SubscriptionPlan
from sales.serializers import SubscriptionPlanSerializer


class SubscriptionPlanViewSet(ReadOnlyModelViewSet):
    """Представление для тарифных планов"""
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    def get_queryset(self):
        # Исключаем пробные тарифы из общего списка (они назначаются автоматически)
        return SubscriptionPlan.objects.filter(is_trial=False)


class SubscribeView(APIView):
    """Представление для оформления подписки"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')

        if not plan_id:
            return Response(
                {"error": "ID плана подписки обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем выбранный план подписки
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Обновляем профиль пользователя
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.subscription_plan = plan
        profile.subscription_start_date = None  # Чтобы save() использовал текущую дату
        profile.subscription_end_date = None  # Будет рассчитано в save()
        profile.is_active = True
        profile.save()

        # Активируем все сайты пользователя
        from constructor.models import CustomSite
        CustomSite.objects.filter(user=request.user).update(is_published=True)

        # Возвращаем обновленный профиль
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MySubscriptionView(APIView):
    """Представление для получения информации о текущей подписке"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)