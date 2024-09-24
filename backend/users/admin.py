from django.contrib import admin

from .models import RegularUser


class RegularUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_subscribed',
        'avatar',
    )


admin.site.register(RegularUser, RegularUserAdmin)
