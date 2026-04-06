from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .services import AnalyticsService

class AnalyticsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        user = request.user
        summary = AnalyticsService.get_summary(user)
        monthly_stats = AnalyticsService.get_monthly_stats(user)
        top_categories = AnalyticsService.get_top_categories(user)
        
        return Response({
            "status": "success",
            "data": {
                "summary": summary,
                "monthly_stats": monthly_stats,
                "top_categories": top_categories
            }
        })
