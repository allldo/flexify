from django.db.models import Model, CharField, DecimalField, TextField, ManyToManyField, PositiveIntegerField

class SubscriptionPlan(Model):
    """Модель тарифного плана"""
    name = CharField(max_length=100, unique=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    description = TextField(blank=True)
    # allowed_blocks = ManyToManyField('constructor.BlockType', related_name='available_in_plans')
    max_sites = PositiveIntegerField(default=1, verbose_name='Максимальное количество сайтов')

    def __str__(self):
        return self.name
