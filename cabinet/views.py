from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cabinet.models import Profile, ActivationCode, CustomUser
from cabinet.serializers import ProfileSerializer, ActivationCodeSerializer, RegisterSerializer, LoginSerializer
from cabinet.service import generate_code
from constructor.models import CustomSite
from sales.models import SubscriptionPlan
from sales.tasks import create_default_trial_subscription


class ProfileView(APIView):
    """Представление для профиля пользователя"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    @extend_schema(request=RegisterSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            code = generate_code()
            activation_code, created = ActivationCode.objects.get_or_create(
                email=email, expired=False, code=code
            )


            send_mail(
                'Подтверждение регистрации Flexify',
                f'Ваш код подтверждения: {activation_code.code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Код подтверждения отправлен на ваш email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(request=LoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.filter(email=serializer.validated_data['email']).first()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": f"{token.key}"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    """Подтверждение кода и выдача токена"""

    @extend_schema(request=ActivationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ActivationCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                activation_code = ActivationCode.objects.get(code=code)
            except ActivationCode.DoesNotExist:
                return Response(data={'result': 'Код не существует'}, status=status.HTTP_400_BAD_REQUEST)
            activation_code.set_code_expired()
            ActivationCode.objects.filter(email=email).update(expired=True)

            user = CustomUser.objects.get(email=email)

            token, created = Token.objects.get_or_create(user=user)

            profile, created = Profile.objects.get_or_create(user=user)

            if created:
                profile.subscription_plan = SubscriptionPlan.objects.get(is_trial=True)
                profile.save()

            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)