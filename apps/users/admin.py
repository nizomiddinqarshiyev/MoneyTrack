from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from apps.wallets.models import Wallet

class WalletInline(admin.TabularInline):
    model = Wallet
    extra = 0
    fields = ('name', 'card_type', 'card_number', 'expire_date', 'cvv', 'balance', 'currency', 'is_active')
    readonly_fields = ('balance', 'created_at')
    can_delete = False

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('phone_number', 'full_name', 'email', 'main_currency', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'main_currency', 'is_superuser')
    search_fields = ('phone_number', 'full_name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'main_currency', 'notifications_enabled')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Brute Force Protection', {'fields': ('is_locked', 'locked_until')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'email', 'main_currency', 'password'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)
    inlines = [WalletInline]

