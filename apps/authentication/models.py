from django.db import models
from django.conf import settings

class LoginAttempt(models.Model):
    phone_number = models.CharField(max_length=13)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    is_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.phone_number} - {self.attempts} attempts"

# OTP will be stored in Redis as requested, but I'll add a model for history/audit if needed.
# Requirement: "stored in Redis". So I won't create a DB table for OTP in authentication unless for record keeping.
# However, the user listed "OTPCode" in "Main tables". So I'll include it.

class OTPCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.email} - {self.code}"
