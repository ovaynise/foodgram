from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import RegularUser


UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio',)}),
)

admin.site.register(RegularUser, UserAdmin)