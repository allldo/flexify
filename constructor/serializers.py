import re

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.fields import ImageField

from .models import (
    CustomSite, Block,
)


class BlockSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=ImageField(),
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

        # if block_type not in ['image', 'profile', 'gif'] and data.:
        #     raise serializers.ValidationError({"type": "Invalid block type."})

        if block_type == 'image' and not images:
            raise serializers.ValidationError({"images": "At least one image is required for image blocks."})
        return attrs

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        block = super().create(validated_data)

        if images:
            image_urls = []
            for image in images:
                default_storage.save(f"block_images/{image.name}", image)
                image_urls.append(f"{settings.BACKEND_URL}/media/block_images/{image.name}")

            validated_data['data'] = {**validated_data.get('data', {}), 'image_urls': image_urls}
            block.data = validated_data['data']
            block.save()

        return block


class CustomSiteSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True)

    class Meta:
        model = CustomSite
        fields = ['id', 'name', 'is_template', 'created_at']

    def validate_name(self, value):
        name = re.sub(r'[^a-zA-Zа-яА-Я0-9-]', '-', value)
        name = re.sub(r'-+', '-', name).strip('-')
        if CustomSite.objects.filter(name=name).exists():
            raise serializers.ValidationError("Сайт с таким именем уже существует")
        return name


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

