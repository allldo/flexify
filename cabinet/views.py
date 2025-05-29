from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cabinet.models import Profile, ActivationCode, CustomUser
from cabinet.serializers import ProfileSerializer, ActivationCodeSerializer, RegisterSerializer, LoginSerializer
from cabinet.service import generate_code
from constructor.models import CustomSite
from sales.tasks import create_default_trial_subscription


class ProfileView(APIView):
    """Представление для профиля пользователя"""
    permission_classes = [IsAuthenticated]

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
            password = serializer.validated_data['password']

            user = CustomUser.objects.create_user(
                email=email,
                password=password
            )

            code = generate_code()
            activation_code, created = ActivationCode.objects.get_or_create(
                email=email,
                defaults={'code': code}
            )

            if not created:
                activation_code.code = code
                activation_code.expired = False
                activation_code.save()

            send_mail(
                'Подтверждение регистрации Flexify',
                f'Ваш код подтверждения: {code}',
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
            email = serializer.validated_data['email']

            # Получаем пользователя (пароль уже проверен в сериализаторе)
            user = CustomUser.objects.get(email=email)

            # Генерация кода и отправка на email
            code = generate_code()
            activation_code, created = ActivationCode.objects.get_or_create(
                email=email,
                defaults={'code': code}
            )

            if not created:
                activation_code.code = code
                activation_code.expired = False
                activation_code.save()

            # Отправляем код на email
            send_mail(
                'Код для входа Flexify',
                f'Ваш код для входа: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Код отправлен на ваш email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    """Подтверждение кода и выдача токена"""

    @extend_schema(request=ActivationCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ActivationCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            activation_code = ActivationCode.objects.filter(email=email, expired=False).first()
            if activation_code and activation_code.get_code == code:
                activation_code.set_code_expired()

                user = CustomUser.objects.get(email=email)

                token, created = Token.objects.get_or_create(user=user)

                # Создаем профиль если его нет
                profile, created = Profile.objects.get_or_create(user=user)

                return Response({"token": token.key}, status=status.HTTP_200_OK)

            return Response({"detail": "Неверный код."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)