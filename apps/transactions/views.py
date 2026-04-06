from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'type': ['exact'],
        'category': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['description']
    ordering_fields = ['created_at', 'amount']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Transaction.objects.none()
        return Transaction.objects.filter(user=self.request.user).select_related('category', 'wallet')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(responses={200: TransactionSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='grouped-by-day')
    def grouped_by_day(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        grouped = queryset.annotate(day=TruncDay('created_at')).values('day', 'type').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('-day')
        return Response(grouped)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
