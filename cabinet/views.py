from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cabinet.models import Profile, ActivationCode
from cabinet.serializers import ProfileSerializer, ActivationCodeSerializer, RegisterSerializer
from cabinet.service import generate_code


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
    def post(self, request, *args, **kwargs):
        # Получаем номер телефона из запроса
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']

            # Генерация кода и отправка
            code = generate_code()
            activation_code = ActivationCode.objects.create(phone_number=phone_number, code=code)
            print(code)
            # Отправляем код на телефон (в данном случае через email, в реальности через SMS API)
            # send_mail(
            #     'Ваш код активации',
            #     f'Ваш код: {code}',
            #     'from@example.com',  # Замените на ваш email
            #     [phone_number],  # Здесь можно заменить на SMS API
            #     fail_silently=False,
            # )

            return Response({"message": "Код отправлен на ваш номер телефона."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        # Получаем номер телефона и код
        serializer = ActivationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']

            # Проверка кода
            activation_code = ActivationCode.objects.filter(phone_number=phone_number, expired=False).first()
            if activation_code.get_code == code:
                # Устанавливаем код как истекший
                activation_code.set_code_expired()
                return Response({"message": "Вы успешно вошли в систему."}, status=status.HTTP_200_OK)

            return Response({"detail": "Неверный код."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)