from django.contrib import admin

from .models import RegularUser


class RegularUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
    )
    search_fields = ('email', 'username')
    empty_value_display = 'Не задано'


admin.site.register(RegularUser, RegularUserAdmin)
