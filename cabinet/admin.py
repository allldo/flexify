from django.contrib import admin

from cabinet.models import CustomUser, ActivationCode, Profile

admin.site.register(CustomUser)

admin.site.register(Profile)
admin.site.register(ActivationCode)