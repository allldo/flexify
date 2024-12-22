import os

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import CustomSite, Block
from .serializers import (
    CustomSiteSerializer, BlockSerializer, CustomSiteFullSerializer, BlockOrderDictSerializer
)


class CustomSiteViewSet(viewsets.ModelViewSet):
    queryset = CustomSite.objects.all()
    serializer_class = CustomSiteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return CustomSite.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CustomSiteFullSerializer(instance)
        return Response(serializer.data)

class TemplateCustomSiteView(APIView):

    def post(self, request, *args, **kwargs):
        site_id = request.data.get('site_id')
        if site_id:
            site = CustomSite.objects.get(id=site_id)
            site_template = site
            site_template.pk = None
            site_template.is_template = True
            site_template.save()

            return Response(CustomSiteSerializer(site_template).data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Site ID is required."}, status=status.HTTP_400_BAD_REQUEST)


class CustomSiteCopyView(APIView):

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
        # фильтр для опубликованных
        custom_site = CustomSite.objects.filter(name=site_name).first()
        if custom_site:
            return Response(CustomSiteFullSerializer(instance=custom_site).data, status=200)
        return Response(data={"message": "site wasn't found"}, status=404)


class ChunkedUploadView(APIView):
    def post(self, request):
        upload_id = request.POST.get("upload_id")
        chunk_number = request.POST.get("chunk_number")
        chunk = request.FILES.get("chunk")

        if not upload_id or chunk_number is None or not chunk:
            return Response({"error": "Invalid data"}, status=400)

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        chunk_path = os.path.join(upload_dir, f"chunk_{chunk_number}")
        with open(chunk_path, "wb") as f:
            for chunk_part in chunk.chunks():
                f.write(chunk_part)

        return Response({"message": f"Chunk {chunk_number} uploaded successfully."})


class AssembleChunksView(APIView):
    def post(self, request):
        upload_id = request.POST.get("upload_id")
        output_filename = request.POST.get("output_filename")

        if not upload_id or not output_filename:
            return Response({"error": "Invalid data"}, status=400)

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", upload_id)
        if not os.path.exists(upload_dir):
            return Response({"error": "Upload ID not found"}, status=404)

        output_path = os.path.join(settings.MEDIA_ROOT, "final", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as final_file:
            for chunk_file in sorted(os.listdir(upload_dir), key=lambda x: int(x.split("_")[1])):
                chunk_path = os.path.join(upload_dir, chunk_file)
                with open(chunk_path, "rb") as cf:
                    final_file.write(cf.read())

        # Удаляем временные файлы
        for chunk_file in os.listdir(upload_dir):
            os.remove(os.path.join(upload_dir, chunk_file))
        os.rmdir(upload_dir)

        return Response({"message": "File assembled successfully.", "file_url": output_path})