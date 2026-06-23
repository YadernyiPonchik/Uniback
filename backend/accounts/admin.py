from django.contrib import admin
from .models import UserAccount

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'gender', 'telegram_id', 'is_staff', 'is_active')
    search_fields = ('email', 'name', 'telegram_id')

admin.site.register(UserAccount, UserAccountAdmin)
