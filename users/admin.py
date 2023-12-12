from django.contrib import admin

from users.models import User, UserConfirmation


@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'phone_number']


admin.site.register(UserConfirmation)
