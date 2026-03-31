from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
  list_display = ('username', 'email', 'phone', 'is_staff', 'created_at')
  list_filter = ('is_staff', 'is_active')
  search_fields = ('username', 'email', 'phone')
  ordering = ('-created_at',)

  fieldsets = UserAdmin.fieldsets + (
    ('Additional Info', {
      'fields': ('phone', 'profile_picture')
    }),
  )