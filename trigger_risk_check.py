import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.transactions.serializers import TransactionSerializer
from apps.wallets.models import Wallet
from rest_framework.test import APIRequestFactory

User = get_user_model()
user = User.objects.get(phone_number='+998912351954')
wallet = user.wallets.first()

if not wallet:
    # Create a dummy wallet if none exists
    wallet = Wallet.objects.create(user=user, balance=1000000, card_number="8600123412341234")

# Mock a request for context
factory = APIRequestFactory()
request = factory.post('/api/transactions/', {})
request.user = user

data = {
    "wallet": wallet.id,
    "type": "expense",
    "amount": 500000, # 5000 UZS
    "description": "Integrated Test Transaction"
}

serializer = TransactionSerializer(data=data, context={'request': request})
try:
    print("Validating transaction...")
    if serializer.is_valid(raise_exception=True):
        print("Transaction is VALID (Approved by Antifraud)")
except Exception as e:
    print(f"Validation Result: {str(e)}")
