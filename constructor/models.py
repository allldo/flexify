from django.db.models import CharField, ForeignKey, CASCADE, Model, \
    PositiveIntegerField, DateTimeField, BooleanField, ManyToManyField, JSONField

from cabinet.models import CustomUser


class CustomSite(Model):
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name='custom_sites')
    name = CharField(max_length=155)
    blocks = ManyToManyField('Block', related_name='custom_sites', blank=True)
    is_template = BooleanField(default=False, verbose_name='Шаблонный сайт')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Block(Model):
    BLOCK_TYPES = (
        ('text', 'Text Block'),
        ('image', 'Image Block'),
        ('video', 'Video Block'),
        ('profile', 'Profile Block'),
        ('product', 'Product Block'),
        ('link', 'Link Block'),
        ('quote', 'Quote Block'),
        ('contacts', 'Contacts Block'),
        ('delimiter', 'Delimiter Block'),
    )

    type = CharField(max_length=50, choices=BLOCK_TYPES, null=True, blank=True)
    order = PositiveIntegerField(default=0)
    data = JSONField(null=True, blank=True)  # Универсальные данные блока
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

#
# class TextBlock(Block):
#     """Текстовый блок"""
#     # title = CharField(max_length=255)
#     content = TextField()
#
#
# class ImageBlock(Block):
#     """Блок с изображением"""
#     image = ImageField(upload_to='image_blocks/')
#     # caption = CharField(max_length=255, null, blank=True)
#
#
# class VideoBlock(Block):
#     """Блок с видео"""
#     video_url = URLField()
#     title = CharField(max_length=255, blank=True)
#
#
# class GifBlock(Block):
#     image = ImageField(upload_to='gif_blocks/')
#
#
# class LinkSocial(Model):
#     url = URLField(max_length=255, null=True, blank=True)
#
#
# class Socials(Block):
#     url = ManyToManyField(LinkSocial)
#
#
# class Profile(Block):
#     title = CharField(max_length=256)
#     description = TextField()
#     image = ImageField(upload_to='profile_blocks/')
#
#
# class Faq(Block):
#     title = CharField(max_length=256)
#
#
# class Product(Block):
#     title = CharField(max_length=256)
#     description = TextField()
#     price = PositiveIntegerField()
#     image = ImageField(upload_to='product_blocks/')
#     button_text =CharField(max_length=256)
#
#
# class Link(Block):
#     title = CharField(max_length=256)
#     link_destination = URLField(max_length=256)
#
#
# class Quote(Block):
#     title = CharField(max_length=256)
#     description = TextField()
#     author = CharField(max_length=256)
#
#
# class Contacts(Block):
#     # дерьмо здесь мб переделать
#     title = CharField(max_length=256)
#     phone_number = CharField(max_length=56)
#     email = EmailField()
#     wpp = CharField(max_length=56)
#     telegram = CharField(max_length=156)
#
# class Delimiter(Block):
#     # тут ссылка на делимитер
#     delimiter_url = CharField(max_length=256)