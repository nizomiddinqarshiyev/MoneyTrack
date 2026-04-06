from django.contrib import admin
from .models import Wallet
from apps.transactions.models import Transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    fk_name = 'wallet'
    extra = 0
    readonly_fields = ('created_at', 'type', 'amount', 'category', 'description')
    ordering = ('-created_at',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'card_type', 'card_number', 'balance', 'currency', 'is_default', 'is_active', 'created_at')
    list_filter = ('card_type', 'currency', 'is_default', 'is_active', 'created_at')
    search_fields = ('name', 'card_number', 'user__phone_number', 'user__full_name')
    autocomplete_fields = ('user',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TransactionInline]
