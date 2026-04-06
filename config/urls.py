from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Apps
    path('api/auth/', include('apps.authentication.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/v1/wallets/', include('apps.wallets.urls')),
    path('api/v1/transactions/', include('apps.transactions.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/currency/', include('apps.currency.urls')),
    path('api/antifraud/', include('apps.antifraud.urls')),
]
