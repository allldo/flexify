from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import (
    CustomSite, Block,
)
class BlockSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
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

        if images:
            data['image_urls'] = [image.url for image in images]
            validated_data['data'] = data

        return super().create(validated_data)

class CustomSiteSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True)

    class Meta:
        model = CustomSite
        fields = ['id', 'user', 'name', 'blocks', 'is_template', 'created_at']