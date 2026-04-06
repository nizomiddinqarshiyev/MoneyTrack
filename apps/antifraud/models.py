from django.db import models
from django.conf import settings

class FaceProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='face_profile')
    face_encoding = models.BinaryField()  # Serialized face encoding (e.g., from face_recognition)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Face Profile for {self.user.full_name}"

class UserLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    ip_address = models.GenericIPAddressField()
    country_code = models.CharField(max_length=5, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'country_code')

    def __str__(self):
        return f"{self.user.full_name} in {self.country_code or 'Unknown'}"

class TransactionRisk(models.Model):
    RISK_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    transaction = models.OneToOneField('transactions.Transaction', on_delete=models.CASCADE, related_name='risk_assessment', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='risk_assessments', null=True)
    amount = models.BigIntegerField(null=True)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='low')
    reasons = models.JSONField(default=list)  # List of reasons for the risk level
    is_verified = models.BooleanField(default=False)
    verification_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Risk assessment for {self.user.full_name}: {self.risk_level}"
