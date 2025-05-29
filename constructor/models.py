from django.db.models import CharField, ForeignKey, CASCADE, Model, \
    PositiveIntegerField, DateTimeField, BooleanField, ManyToManyField, JSONField, SET_NULL, ImageField

from cabinet.models import CustomUser


class CustomSite(Model):
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name='custom_sites')
    name = CharField(max_length=155)
    blocks = ManyToManyField('Block', related_name='custom_sites', blank=True)
    is_template = BooleanField(default=False, verbose_name='Шаблонный сайт')
    created_at = DateTimeField(auto_now_add=True)
    template = ForeignKey('self', on_delete=SET_NULL, null=True, blank=True, related_name='derived_sites')
    qr_code = ImageField(upload_to='qr_codes/', blank=True, null=True, verbose_name='QR код')
    is_published = BooleanField(default=False)

    def __str__(self):
        return self.name

    def copy_from_template(self):
        """Создает копию блоков из шаблона"""
        if self.template:
            self.blocks.set(self.template.blocks.all())

    def save(self, *args, **kwargs):
        # Сначала сохраняем объект, чтобы получить ID если это новый объект
        super().save(*args, **kwargs)

        # Генерируем QR-код если его еще нет
        if not self.qr_code:
            from constructor.services import generate_and_save_qr_code
            generate_and_save_qr_code(self)

    @property
    def is_available(self):
        """
        Проверяет, доступен ли сайт на основе статуса подписки пользователя
        """
        try:
            profile = self.user.profile
            # Если подписка активна и не истекла, сайт доступен
            return profile.is_active and not profile.is_subscription_expired
        except Exception:
            # Если у пользователя нет профиля или другая ошибка
            return False

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
        ('gallery', 'Gallery Block'),
        ('mix', 'Mix block')
    )

    type = CharField(max_length=50, choices=BLOCK_TYPES, null=True, blank=True)
    order = PositiveIntegerField(default=0)
    data = JSONField(null=True, blank=True)  # Универсальные данные блока
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def get_owner(self):
        sites = self.custom_sites.all()
        if sites.exists():
            return sites.first().user
        return None

    def __str__(self):
        return self.type if self.type else 'Block'
