from rest_framework import serializers
from .models import Transaction, Category
from apps.wallets.serializers import WalletSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon')

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    sender_name = serializers.CharField(source='user.full_name', read_only=True)
    sender_phone = serializers.CharField(source='user.phone_number', read_only=True)
    receiver_name = serializers.CharField(source='receiver.full_name', read_only=True)
    receiver_phone = serializers.CharField(source='receiver.phone_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = (
            'id', 'wallet', 'type', 'amount', 'category', 'category_name', 
            'description', 'receiver', 'receiver_wallet',
            'sender_name', 'sender_phone', 'receiver_name', 'receiver_phone',
            'created_at'
        )
        read_only_fields = ('id', 'created_at', 'sender_name', 'sender_phone', 'receiver_name', 'receiver_phone')

    def validate(self, data):
        user = self.context['request'].user
        wallet = data.get('wallet')
        amount = int(data.get('amount'))
        transaction_type = data.get('type')

        if wallet and wallet.user != user:
            raise serializers.ValidationError({"wallet": "Wallet does not belong to the user."})
            
        if transaction_type in ['expense', 'transfer']:
            if wallet.balance < amount:
                raise serializers.ValidationError({
                    "amount": f"Insufficient funds. Required: {amount} tiyin, Available: {wallet.balance} tiyin."
                })

        if transaction_type == 'transfer':
            receiver = data.get('receiver')
            receiver_wallet = data.get('receiver_wallet')

            if not receiver or not receiver_wallet:
                raise serializers.ValidationError("Receiver and Receiver Wallet are required for transfers.")
            
            if wallet == receiver_wallet:
                raise serializers.ValidationError({"receiver_wallet": "Cannot transfer to the same wallet."})
                
        if receiver_wallet.user.id != receiver.id:
                raise serializers.ValidationError({"receiver_wallet": "The selected receiver wallet does not belong to the selected receiver."})
                
        # Risk assessment integration
        from apps.antifraud.external_service import ExternalAntifraudService
        from apps.antifraud.exceptions import BiometricAuthRequired
        from apps.antifraud.models import TransactionRisk

        # Get country code from headers if available
        request = self.context.get('request')
        country_code = request.headers.get('X-Country-Code') if request else None

        # Check if there's a verified risk assessment for this user and amount within last 10 mins
        is_already_verified = TransactionRisk.objects.filter(
            user=user,
            amount=amount,
            is_verified=True,
            verification_time__gte=timezone.now() - timedelta(minutes=10)
        ).exists()

        if not is_already_verified:
            # Prepare data for external check
            ip_address = request.META.get('REMOTE_ADDR') if request else '0.0.0.0'
            device_id = request.headers.get('X-Device-ID', 'unknown') if request else 'unknown'
            
            result = ExternalAntifraudService.check_transaction_risk(
                user=user,
                amount=amount,
                transaction_type=transaction_type,
                wallet=wallet,
                receiver_wallet=data.get('receiver_wallet'),
                ip_address=ip_address,
                device_id=device_id
            )
            
            decision = result.get('decision', 'APPROVED')
            score = result.get('score', 0)
            reasons = result.get('results', [])
            
            if decision == 'DECLINED':
                raise serializers.ValidationError({
                    "non_field_errors": f"Transaction declined due to security risks: {', '.join(reasons)}"
                })
            
            if decision == 'OTP_REQUIRED':
                # Create a pending risk assessment to track this
                TransactionRisk.objects.create(
                    user=user,
                    amount=amount,
                    risk_level='medium',
                    reasons=reasons,
                    is_verified=False
                )
                raise BiometricAuthRequired(
                    detail=f"Risk detected ({score}): {', '.join(reasons)}. Biometric authentication required.",
                    reasons=reasons
                )

        return data
