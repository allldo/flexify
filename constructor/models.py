from django.db.models import CharField, ImageField, URLField, TextField, ForeignKey, CASCADE, Model, \
    PositiveIntegerField, DateTimeField, BooleanField, ManyToManyField

from cabinet.models import CustomUser


class BlockType(Model):
    """Тип блока (например, текстовый, изображение и т.д.)"""
    name = CharField(max_length=50, unique=True)
    description = TextField(blank=True)

    def __str__(self):
        return self.name


class CustomSite(Model):
    """Мини-сайт пользователя"""
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name='custom_sites')
    name = CharField(max_length=155)
    blocks = ManyToManyField('Block', related_name='custom_sites')
    is_template = BooleanField(default=False, verbose_name='Шаблонный сайт')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def can_add_block(self, block_type: BlockType) -> bool:
        """Проверяет, можно ли добавить блок в зависимости от плана"""
        return block_type in self.user.profile.subscription_plan.allowed_blocks.all()


class Block(Model):
    """Базовый блок"""
    block_type = ForeignKey(BlockType, on_delete=CASCADE, related_name='blocks')
    order = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    class_of_block = CharField(max_length=350, null=True, blank=True)

    class Meta:
        ordering = ['order']


class TextBlock(Block):
    """Текстовый блок"""
    # title = CharField(max_length=255)
    content = TextField()


class ImageBlock(Block):
    """Блок с изображением"""
    image = ImageField(upload_to='image_blocks/')
    # caption = CharField(max_length=255, null, blank=True)


class VideoBlock(Block):
    """Блок с видео"""
    video_url = URLField()
    title = CharField(max_length=255, blank=True)


class GifBlock(Block):
    image = ImageField(upload_to='gif_blocks/')


class Socials(Block):
    pass


class Profile(Block):
    pass


class Faq(Block):
    pass


class Product(Block):
    pass


class Link(Block):
    pass


class Quote(Block):
    pass


class Contacts(Block):
    pass


class Delimiter(Block):
    pass