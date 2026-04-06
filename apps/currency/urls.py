from django.urls import path
from .views import CurrencyRatesView

urlpatterns = [
    path('rates/', CurrencyRatesView.as_view(), name='currency-rates'),
]
