from rest_framework import serializers
from .models import (
    BlockType,
    CustomSite,
    TextBlock,
    ImageBlock,
    VideoBlock,
)

class BlockTypeSerializer(serializers.ModelSerializer):
    """Сериализатор для типов блоков"""

    class Meta:
        model = BlockType
        fields = ['id', 'name', 'description']



class BlockSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для блоков"""
    block_type = BlockTypeSerializer(read_only=True)

    class Meta:
        model = None  # Устанавливается в наследниках
        fields = ['id', 'block_type', 'order', 'created_at']


class TextBlockSerializer(BlockSerializer):
    """Сериализатор для текстовых блоков"""

    class Meta:
        model = TextBlock
        fields = BlockSerializer.Meta.fields + ['title', 'content']


class ImageBlockSerializer(BlockSerializer):
    """Сериализатор для блоков с изображениями"""

    class Meta:
        model = ImageBlock
        fields = BlockSerializer.Meta.fields + ['image', 'caption']


class VideoBlockSerializer(BlockSerializer):
    """Сериализатор для блоков с видео"""

    class Meta:
        model = VideoBlock
        fields = BlockSerializer.Meta.fields + ['video_url', 'title']


class CustomSiteSerializer(serializers.ModelSerializer):
    """Сериализатор для мини-сайтов"""
    blocks = serializers.SerializerMethodField()
    user = serializers.StringRelatedField()

    class Meta:
        model = CustomSite
        fields = ['id', 'user', 'name', 'blocks', 'is_template', 'created_at']

    def get_blocks(self, obj):
        """Собирает все блоки сайта и сериализует их"""
        block_serializers = {
            'TextBlock': TextBlockSerializer,
            'ImageBlock': ImageBlockSerializer,
            'VideoBlock': VideoBlockSerializer
        }
        serialized_blocks = []
        for block in obj.blocks.all():
            block_type = block.block_type.name
            serializer_class = block_serializers.get(block_type)
            if serializer_class:
                serializer = serializer_class(block)
                serialized_blocks.append(serializer.data)
        return serialized_blocks
