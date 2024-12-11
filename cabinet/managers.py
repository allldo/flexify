from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be provided")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.save(using=self._db)
        return user