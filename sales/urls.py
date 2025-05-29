from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sales.views import SubscriptionPlanViewSet, SubscribeView, MySubscriptionView

router = DefaultRouter()
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')
urlpatterns = [
path('', include(router.urls)),

    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('my-subscription/', MySubscriptionView.as_view(), name='my-subscription'),
]