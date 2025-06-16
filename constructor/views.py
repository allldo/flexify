
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from cabinet.models import Profile
from .models import CustomSite, Block
from .permissions import CustomPermission, IsSiteOwnerPermission
from .serializers import (
    CustomSiteSerializer, BlockSerializer, CustomSiteFullSerializer, BlockOrderDictSerializer, ThemeChangeSerializer
)


class CustomSiteViewSet(viewsets.ModelViewSet):
    serializer_class = CustomSiteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        # Проверяем, активна ли подписка пользователя
        profile = Profile.objects.filter(user=self.request.user).first()

        if not profile or not profile.subscription_plan:
            raise PermissionDenied("У вас нет активной подписки для создания сайтов")

        if profile.is_subscription_expired:
            raise PermissionDenied("Ваша подписка истекла")

        # Проверяем, не превышено ли максимальное количество сайтов
        current_sites_count = CustomSite.objects.filter(user=self.request.user).count()
        max_sites = profile.subscription_plan.max_sites

        if current_sites_count >= max_sites:
            raise PermissionDenied(
                f"Вы достигли максимального количества сайтов ({max_sites}) для вашего тарифного плана")

        # Если все проверки пройдены, создаем сайт
        serializer.save(user=self.request.user, is_published=True)

    def get_queryset(self):
        return CustomSite.objects.filter(user=self.request.user)

class TemplateCustomSiteView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site_id')
        template_id = request.data.get('template_id')
        if site_id and template_id:
            site = CustomSite.objects.get(id=site_id)
            site.template = CustomSite.objects.get(id=template_id)
            site.save()
            site.copy_from_template()

            return Response(CustomSiteSerializer(site).data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Site ID is required."}, status=status.HTTP_400_BAD_REQUEST)


class CustomSiteCopyView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site_id')
        if site_id:
            site = CustomSite.objects.get(id=site_id)
            site_copy = site
            site_copy.pk = None
            site_copy.save()

            return Response(CustomSiteSerializer(site_copy).data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Site ID is required."}, status=status.HTTP_400_BAD_REQUEST)


class BlockView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSiteOwnerPermission]

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


class BlockViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [CustomPermission]

    def retrieve(self, request, pk):
        block = get_object_or_404(Block, id=pk)
        serializer = BlockSerializer(block)
        return Response({"block": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        request=BlockSerializer,
        responses={200: BlockSerializer},
        description="Редактирование блока"
    )
    def partial_update(self, request, pk):
        block = get_object_or_404(Block, id=pk)
        serializer = BlockSerializer(block, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Block updated successfully", "block": serializer.data},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        responses={204: None},
        description="Удаление блока по ID"
    )
    def destroy(self, request, pk):
        block = get_object_or_404(Block, id=pk)
        block.delete()
        return Response({"detail": "Block deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class ReArrangeBlocksView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [CustomPermission]
    @extend_schema(
        request=BlockOrderDictSerializer,
        responses={201: BlockSerializer},
        description="Добавление блока"
    )

    def post(self, request):
        serializer = BlockOrderDictSerializer(data=request.data)

        if serializer.is_valid():
            updated_blocks = serializer.update_block_orders()
            return Response(
                {
                    "detail": "Orders updated successfully",
                    "updated_blocks": {block.id: block.order for block in updated_blocks},
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicSiteView(APIView):
    def get(self, request, site_name):
        custom_site = CustomSite.objects.filter(name=site_name).first()

        if not custom_site:
            return Response(data={"message": "Сайт не найден"}, status=404)

        # Проверяем, опубликован ли сайт и активна ли подписка
        if not custom_site.is_published:
            return Response(data={"message": "Сайт не опубликован"}, status=403)

        # Проверяем доступность сайта (статус подписки)
        if not custom_site.is_available and not custom_site.is_template:
            return Response(
                data={"message": "Сайт недоступен из-за истекшей подписки"},
                status=402  # Payment Required
            )

        return Response(CustomSiteFullSerializer(instance=custom_site).data, status=200)


class ThemeChangeAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSiteOwnerPermission]

    @extend_schema(request=ThemeChangeSerializer)
    def post(self, request, site_id):
        serialized = ThemeChangeSerializer(request.data)
        if serialized.is_valid():
            theme = serialized.theme
            site = CustomSite.objects.get(id=site_id)
            site.theme = theme
            site.save()

            return Response(data={"success": "Theme changed successfully"}, status=200)

        return Response(data={"error": serialized.errors}, status=400)