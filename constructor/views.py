from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import CustomSite, Block
from .serializers import (
    CustomSiteSerializer, BlockSerializer
)


class CustomSiteViewSet(viewsets.ModelViewSet):
    """Представление для кастомных сайтов"""
    queryset = CustomSite.objects.all()
    serializer_class = CustomSiteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

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



class BlockView(APIView):
    @extend_schema(
        request=BlockSerializer,
        responses={201: BlockSerializer},
        description="Добавление блока"
    )
    def post(self, request, site_id):
        site = get_object_or_404(CustomSite, id=site_id)
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            block = serializer.save()
            site.blocks.add(block)
            return Response({"detail": "Block added successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=BlockSerializer,
        responses={200: BlockSerializer},
        description="Редактирование блока"
    )
    def patch(self, request, site_id, block_id):
        site = get_object_or_404(CustomSite, id=site_id)
        block = get_object_or_404(Block, id=block_id, custom_sites=site)

        serializer = BlockSerializer(block, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Block updated successfully", "block": serializer.data},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DeleteBlockView(APIView):
    def delete(self, request, site_id, block_id):
        site = get_object_or_404(CustomSite, id=site_id)
        block = get_object_or_404(Block, id=block_id, custom_sites=site)

        block.delete()

        return Response({"detail": "Block deleted successfully"}, status=status.HTTP_204_NO_CONTENT)