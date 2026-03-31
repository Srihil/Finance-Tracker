from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display  = ('icon', 'name', 'type', 'user', 'is_default', 'created_at')
  list_filter   = ('type', 'is_default')
  search_fields = ('name',)
  ordering      = ('type', 'name')

  fieldsets = (
    ('Category Info', {
      'fields': ('name', 'type', 'icon', 'color')
    }),
    ('Ownership', {
      'fields': ('user', 'is_default')
    }),
  )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
  list_display  = (
    'description', 'user', 'transaction_type',
    'amount', 'category', 'date', 'created_at'
  )
  list_filter   = ('transaction_type', 'date', 'category')
  search_fields = ('description', 'user__username', 'user__email')
  ordering      = ('-date',)
  date_hierarchy = 'date'  

  fieldsets = (
    ('Transaction Info', {
      'fields': ('user', 'transaction_type', 'amount', 'description', 'date')
    }),
    ('Category & Notes', {
      'fields': ('category', 'notes')
    }),
  )