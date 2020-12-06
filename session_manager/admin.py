from django.contrib import admin

from session_manager.models import UserToken

class UserTokenAdmin(admin.ModelAdmin):
    fields = [
        'user',
        'token',
        'token_type',
        'expiration',
        'link',
    ]
    readonly_fields = ['link', ]

admin.site.register(UserToken, UserTokenAdmin)
