from django.db import models
from django.conf import settings

class Wallet(models.Model):
    CARD_TYPES = (
        ('uzcard', 'Uzcard'),
        ('humo', 'Humo'),
        ('visa', 'Visa'),
        ('virtual', 'Virtual'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wallets', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Main Wallet')
    card_type = models.CharField(max_length=20, choices=CARD_TYPES, default='virtual')
    card_number = models.CharField(max_length=16, unique=True, null=True, blank=True)
    expire_date = models.CharField(max_length=5, null=True, blank=True)  # MM/YY
    cvv = models.CharField(max_length=3, null=True, blank=True)
    
    balance = models.BigIntegerField(default=0)  # Amount in tiyins (1 UZS = 100 tiyins)
    currency = models.CharField(max_length=3, default='UZS')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.phone_number}'s {self.name} ({self.balance} {self.currency})"
