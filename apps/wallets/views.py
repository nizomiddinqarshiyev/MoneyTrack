from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Wallet
from .serializers import WalletSerializer, TopUpSerializer, WalletSearchSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='card_number', description='Card number or partial number to search for', required=True, type=str)
        ],
        responses={200: WalletSearchSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        card_number = request.query_params.get('card_number')
        if not card_number:
            return Response({"error": "card_number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove any non-digit characters (spaces, dashes, etc.)
        card_number = ''.join(filter(str.isdigit, card_number))
        
        if len(card_number) < 4:
            return Response({"error": "Please enter at least 4 digits"}, status=status.HTTP_400_BAD_REQUEST)

        # We search across all wallets, using icontains for partial match
        wallets = Wallet.objects.filter(card_number__icontains=card_number, is_active=True)[:15]
        
        serializer = WalletSearchSerializer(wallets, many=True)
        return Response(serializer.data)
