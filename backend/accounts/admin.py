from django.contrib import admin
from .models import UserAccount


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'gender', 'telegram_id', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'gender', 'cohort')
    search_fields = ('email', 'name', 'telegram_id')
    autocomplete_fields = ('cohort',)
    ordering = ('email',)
