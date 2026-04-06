from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.transactions.models import Transaction
from apps.wallets.services import WalletService

@receiver(post_save, sender=Transaction)
def handle_transaction_save(sender, instance, created, **kwargs):
    """
    Automatically updates wallet balance when a transaction is saved.
    """
    if created:
        if instance.type == 'transfer' and instance.receiver_wallet:
            WalletService.transfer(instance.wallet.id, instance.receiver_wallet.id, instance.amount)
        else:
            WalletService.update_balance(instance.wallet.id, instance.amount, instance.type)
    else:
        # For updates, we would need to handle the difference. 
        # For simplicity in this initial version, we assume transactions are immutable or 
        # we'd implement a more complex diffing logic.
        pass

@receiver(post_delete, sender=Transaction)
def handle_transaction_delete(sender, instance, **kwargs):
    """
    Reverts wallet balance when a transaction is deleted.
    """
    if instance.type == 'transfer' and instance.receiver_wallet:
        WalletService.update_balance(instance.wallet.id, instance.amount, 'income')
        WalletService.update_balance(instance.receiver_wallet.id, instance.amount, 'expense')
    else:
        # Reverse the type for deletion
        reverse_type = 'expense' if instance.type == 'income' else 'income'
        WalletService.update_balance(instance.wallet.id, instance.amount, reverse_type)
