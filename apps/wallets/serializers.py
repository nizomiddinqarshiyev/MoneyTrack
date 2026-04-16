from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    masked_number = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = (
            'id', 'name', 'card_type', 'card_number', 'expire_date', 
            'cvv', 'balance', 'currency', 'is_default', 'is_active', 
            'masked_number', 'created_at'
        )
        read_only_fields = ('id', 'balance', 'created_at', 'masked_number')
        extra_kwargs = {
            'card_number': {'write_only': True},
            'cvv': {'write_only': True},
        }

    @extend_schema_field(str)
    def get_masked_number(self, obj):
        if obj.card_number and len(obj.card_number) >= 12:
            return f"{obj.card_number[:4]} **** **** {obj.card_number[-4:]}"
        return obj.card_number

    def validate_card_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Card number must contain only digits.")
        if value and len(value) not in [16, 18]:
            raise serializers.ValidationError("Card number must be 16 or 18 digits.")
        return value

    def validate_expire_date(self, value):
        import re
        if value and not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', value):
            raise serializers.ValidationError("Expire date must be in MM/YY format.")
        return value

class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal('0.01'))

class WalletSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    masked_number = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ('id', 'full_name', 'masked_number', 'card_type')

    @extend_schema_field(str)
    def get_masked_number(self, obj):
        if obj.card_number and len(obj.card_number) >= 12:
            return f"{obj.card_number[:4]} **** **** {obj.card_number[-4:]}"
        return obj.card_number
