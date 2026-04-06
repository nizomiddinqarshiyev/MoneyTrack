from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_default')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'wallet', 'type', 'amount', 'category')
    list_filter = ('type', 'category', 'wallet', 'created_at')
    search_fields = ('description', 'user__phone_number', 'wallet__name')
    autocomplete_fields = ('user', 'wallet', 'category')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
