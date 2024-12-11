from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import CustomSite, BlockType, TextBlock, ImageBlock, VideoBlock
from .serializers import (
    CustomSiteSerializer,
    TextBlockSerializer,
    ImageBlockSerializer,
    VideoBlockSerializer, BlockTypeSerializer
)




class BlockTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для типов блоков"""
    queryset = BlockType.objects.all()
    serializer_class = BlockTypeSerializer



class CustomSiteViewSet(viewsets.ModelViewSet):
    """Представление для кастомных сайтов"""
    queryset = CustomSite.objects.all()
    serializer_class = CustomSiteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """При создании нового сайта привязываем его к пользователю"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Фильтрация сайтов по пользователю"""
        return CustomSite.objects.filter(user=self.request.user)


class TemplateCustomSiteView(APIView):
    """Представление для шаблонов сайтов"""

    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site_id')
        if site_id:
            # Копируем сайт по id и помечаем как шаблон
            site = CustomSite.objects.get(id=site_id)
            site_template = site
            site_template.pk = None  # Создаем новый объект с тем же содержанием
            site_template.is_template = True
            site_template.save()

            return Response(CustomSiteSerializer(site_template).data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Site ID is required."}, status=status.HTTP_400_BAD_REQUEST)


class TextBlockViewSet(viewsets.ModelViewSet):
    """Представление для текстовых блоков"""
    queryset = TextBlock.objects.all()
    serializer_class = TextBlockSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """При создании блока привязываем его к пользователю"""
        # Вы можете добавить дополнительную логику для блоков, например, привязку к сайту
        serializer.save()


class ImageBlockViewSet(viewsets.ModelViewSet):
    """Представление для блоков с изображениями"""
    queryset = ImageBlock.objects.all()
    serializer_class = ImageBlockSerializer
    permission_classes = [IsAuthenticated]


class VideoBlockViewSet(viewsets.ModelViewSet):
    """Представление для видео блоков"""
    queryset = VideoBlock.objects.all()
    serializer_class = VideoBlockSerializer
    permission_classes = [IsAuthenticated]


class CustomSiteCopyView(APIView):
    """Представление для копирования кастомного сайта"""

    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site_id')
        if site_id:
            # Копируем сайт по id
            site = CustomSite.objects.get(id=site_id)
            site_copy = site
            site_copy.pk = None  # Создаем новый объект с тем же содержанием
            site_copy.save()

            # Можно добавить логику для копирования всех блоков (это будет сделано в методах create_block для каждого типа блока)
            return Response(CustomSiteSerializer(site_copy).data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Site ID is required."}, status=status.HTTP_400_BAD_REQUEST)
