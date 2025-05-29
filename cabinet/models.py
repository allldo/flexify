from django.contrib.auth.models import AbstractUser
from django.db.models import Model, OneToOneField, CASCADE, SET_NULL, DateField, ForeignKey, BooleanField, CharField, \
    EmailField
from django.utils import timezone

from cabinet.managers import UserManager
from cabinet.service import generate_code
from sales.models import SubscriptionPlan


class CustomUser(AbstractUser):
    phone_number = CharField(max_length=30)
    email = EmailField(unique=True)
    username = None
    objects = UserManager()
    REQUIRED_FIELDS = []

    USERNAME_FIELD = 'email'


class Profile(Model):
    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name='profile')
    subscription_plan = ForeignKey(SubscriptionPlan, on_delete=SET_NULL, null=True)
    subscription_start_date = DateField(auto_now_add=True)
    subscription_end_date = DateField(null=True, blank=True)
    is_active = BooleanField(default=True, help_text='Активна ли подписка')

    def __str__(self):
        return f"Profile of {self.user.phone_number}"

    def save(self, *args, **kwargs):
        # Если назначен план подписки и нет даты окончания
        if self.subscription_plan and not self.subscription_end_date:
            # Рассчитываем дату окончания подписки
            days = self.subscription_plan.duration_days
            start_date = self.subscription_start_date or timezone.now().date()
            self.subscription_end_date = start_date + timezone.timedelta(days=days)

        super().save(*args, **kwargs)

    @property
    def is_subscription_expired(self):
        """Проверяет, истекла ли подписка"""
        if not self.subscription_end_date:
            return True
        return timezone.now().date() > self.subscription_end_date


class ActivationCode(Model):
    email = CharField(max_length=255)
    expired = BooleanField(default=False)
    code = CharField(max_length=4, default=generate_code)

    @property
    def get_code(self):
        return self.code

    def set_code_expired(self):
        self.expired = True
        self.save()
