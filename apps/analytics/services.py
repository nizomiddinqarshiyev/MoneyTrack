from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.transactions.models import Transaction
from apps.wallets.models import Wallet

class AnalyticsService:
    @staticmethod
    def get_summary(user):
        """
        Returns a summary of income, expense, and savings.
        """
        transactions = Transaction.objects.filter(user=user)
        
        income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return {
            'total_income': income,
            'total_expense': expense,
            'savings_indicator': income - expense,
        }

    @staticmethod
    def get_monthly_stats(user):
        """
        Returns monthly income vs expense for the last 6 months.
        """
        six_months_ago = timezone.now() - timedelta(days=180)
        stats = Transaction.objects.filter(
            user=user, 
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month', 'type').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        return stats

    @staticmethod
    def get_top_categories(user, limit=5):
        """
        Returns the top categories by expense amount.
        """
        return Transaction.objects.filter(
            user=user, 
            type='expense'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:limit]
