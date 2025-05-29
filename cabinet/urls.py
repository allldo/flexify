from django.urls import path

from cabinet.views import ProfileView, RegisterView, LoginView, VerifyCodeView
from rest_framework.authtoken import views

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('api-token-auth/', LoginView.as_view()),
]