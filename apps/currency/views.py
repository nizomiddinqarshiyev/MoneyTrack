from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .services import CurrencyService

class CurrencyRatesView(APIView):
    # In some cases rates can be public, but requirement says User Profile has main currency,
    # so keeping it authenticated.
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        rates = CurrencyService.get_latest_rates()
        return Response({
            "status": "success",
            "data": rates
        })
