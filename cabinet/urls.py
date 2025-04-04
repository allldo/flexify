from django.urls import path

from cabinet.views import ProfileView, RegisterView, LoginView
from rest_framework.authtoken import views

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
    path('api-token-auth/', LoginView.as_view()),
]