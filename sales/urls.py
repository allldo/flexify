from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sales.views import SubscriptionPlanViewSet

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')
urlpatterns = [
path('', include(router.urls)),
]