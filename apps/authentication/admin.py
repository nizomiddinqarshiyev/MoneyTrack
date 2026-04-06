from django.contrib import admin
from .models import LoginAttempt, OTPCode

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'attempts', 'last_attempt', 'is_locked', 'locked_until')
    list_filter = ('is_locked',)
    search_fields = ('phone_number', 'ip_address')
    readonly_fields = ('last_attempt',)

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
