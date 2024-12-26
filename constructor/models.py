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
        ('gif', 'Gif Block'),
        ('qanda', 'QandA Block'),
        ('social', 'Social Block'),
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
