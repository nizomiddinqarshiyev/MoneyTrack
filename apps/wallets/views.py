from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Wallet
from .serializers import WalletSerializer, TopUpSerializer
from .services import WalletService

class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Wallet.objects.none()
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(request=TopUpSerializer, responses={200: WalletSerializer})
    @action(detail=True, methods=['post'], url_path='topup')
    def topup(self, request, pk=None):
        wallet = self.get_object()
        serializer = TopUpSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            WalletService.topup(wallet.id, amount)
            return Response({"status": "success", "new_balance": wallet.balance})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
