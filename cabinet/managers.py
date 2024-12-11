from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be provided")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be provided")
        user = self.model(phone_number=phone_number)
        user.username = f"admin {datetime.now()}"
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user