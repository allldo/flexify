from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers
import base64
from .models import (
    CustomSite, Block,
)

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)

class BlockSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=Base64ImageField(),
        write_only=True,
        required=False
    )
    class Meta:
        model = Block
        fields = ['id', 'type', 'order', 'data', 'created_at', 'images']

    def validate(self, attrs):
        block_type = attrs.get('type')
        data = attrs.get('data', {})
        images = attrs.get('images', [])

        if block_type == 'image' and not images:
            raise serializers.ValidationError({"images": "At least one image is required for image blocks."})

        return attrs

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        data = validated_data.get('data', {})

        # Сохраняем изображения и получаем их URL
        if images:
            image_urls = []
            for image in images:
                filename = f"blocks/{uuid4().hex}.jpg"  # Уникальное имя файла
                saved_image_path = default_storage.save(filename, ContentFile(image.read()))  # Сохраняем файл
                image_urls.append(default_storage.url(saved_image_path))  # Получаем URL сохраненного файла

            data['image_urls'] = image_urls
            validated_data['data'] = data

        return super().create(validated_data)

class CustomSiteSerializer(serializers.ModelSerializer):
    # blocks = BlockSerializer(many=True)

    class Meta:
        model = CustomSite
        fields = ['id', 'name', 'is_template', 'created_at']


class CustomSiteFullSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True)

    class Meta:
        model = CustomSite
        fields = ['id', 'name', 'blocks','is_template', 'created_at']


class BlockOrderDictSerializer(serializers.Serializer):
    blocks = serializers.DictField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Словарь, где ключ — ID блока, а значение — новый порядок."
    )

    def validate_blocks(self, value):
        invalid_ids = [block_id for block_id in value.keys() if not Block.objects.filter(id=block_id).exists()]
        if invalid_ids:
            raise serializers.ValidationError(f"Блоки с ID {invalid_ids} не существуют.")
        return value

    def update_block_orders(self):
        validated_data = self.validated_data["blocks"]
        updated_blocks = []
        for block_id, order in validated_data.items():
            block = Block.objects.get(id=block_id)
            block.order = order
            block.save()
            updated_blocks.append(block)
        return updated_blocks