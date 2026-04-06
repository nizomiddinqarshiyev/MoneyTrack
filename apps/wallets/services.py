from rest_framework.exceptions import ValidationError
from django.db import transaction
from apps.wallets.models import Wallet

class WalletService:
    @staticmethod
    @transaction.atomic
    def update_balance(wallet_id, amount, transaction_type):
        """
        Updates the wallet balance based on the transaction type.
        Amount is expected in tiyins (integer).
        """
        wallet = Wallet.objects.select_for_update().get(id=wallet_id)
        amount = int(amount)
        
        if transaction_type == 'income':
            wallet.balance += amount
        elif transaction_type == 'expense' or transaction_type == 'transfer':
            if wallet.balance < amount:
                raise ValidationError(f"Insufficient funds in {wallet.name}. Required: {amount} tiyin, Available: {wallet.balance} tiyin.")
            wallet.balance -= amount
        
        wallet.save()
        return wallet

    @staticmethod
    @transaction.atomic
    def topup(wallet_id, amount):
        """
        Directly tops up the wallet balance.
        """
        wallet = Wallet.objects.select_for_update().get(id=wallet_id)
        wallet.balance += int(amount)
        wallet.save()
        return wallet

    @staticmethod
    @transaction.atomic
    def transfer(sender_wallet_id, receiver_wallet_id, amount):
        """
        Processes a transfer between two wallets.
        """
        amount = int(amount)
        if amount <= 0:
            raise ValidationError("Transfer amount must be positive.")

        sender_wallet = Wallet.objects.select_for_update().get(id=sender_wallet_id)
        receiver_wallet = Wallet.objects.select_for_update().get(id=receiver_wallet_id)

        if sender_wallet.balance < amount:
            raise ValidationError(f"Insufficient funds for transfer. Available: {sender_wallet.balance} tiyin.")

        sender_wallet.balance -= amount
        receiver_wallet.balance += amount

        sender_wallet.save()
        receiver_wallet.save()
        return sender_wallet, receiver_wallet

    @staticmethod
    def create_default_wallet(user):
        """
        Creates the initial default wallet for a new user.
        """
        return Wallet.objects.create(
            user=user,
            name="Main Wallet",
            balance=0,
            currency="UZS",
            is_default=True
        )
