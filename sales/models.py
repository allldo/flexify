from django.db.models import Model, CharField, DecimalField, TextField, ManyToManyField, PositiveIntegerField, \
    BooleanField, IntegerField


class SubscriptionPlan(Model):
    """Модель тарифного плана"""
    PERIOD_CHOICES = (
        ('trial', 'Пробный период'),
        ('monthly', 'Месячный'),
        ('yearly', 'Годовой'),
    )

    name = CharField(max_length=100, unique=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    description = TextField(blank=True)
    period = CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    duration_days = IntegerField(default=30, help_text='Длительность подписки в днях')
    is_trial = BooleanField(default=False, help_text='Является ли тариф пробным')
    max_sites = PositiveIntegerField(default=1, verbose_name='Максимальное количество сайтов')

    def __str__(self):
        return f"{self.name} {self.price} {self.period}"
