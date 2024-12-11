from django.contrib.auth.models import AbstractUser
from django.db.models import Model, OneToOneField, CASCADE, SET_NULL, DateField, ForeignKey, BooleanField
from rest_framework.fields import CharField

from cabinet.service import generate_code
from sales.models import SubscriptionPlan


class CustomUser(AbstractUser):
    phone_number = CharField(max_length=30)


class Profile(Model):
    user = OneToOneField(CustomUser, on_delete=CASCADE, related_name='profile')
    subscription_plan = ForeignKey(SubscriptionPlan, on_delete=SET_NULL, null=True)
    subscription_start_date = DateField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class ActivationCode(Model):
    phone_number = CharField(max_length=100, unique=True)
    expired = BooleanField(default=False)
    code = CharField(max_length=4, default=generate_code)

    @property
    def get_code(self):
        return self.code

    def set_code_expired(self):
        self.expired = True
        self.save()
