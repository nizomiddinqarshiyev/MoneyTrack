import requests
from datetime import datetime

class CurrencyService:
    @staticmethod
    def get_latest_rates():
        """
        Fetches real-time exchange rates from CBU.uz
        URL: https://cbu.uz/uz/arkhiv-kursov-valyut/json/
        """
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # CBU returns an array of currencies. We filter for USD, EUR, RUB.
            interesting_currencies = ['USD', 'EUR', 'RUB']
            rates = {}
            for item in data:
                if item['Ccy'] in interesting_currencies:
                    rates[item['Ccy']] = float(item['Rate'])
            
            return {
                "base": "UZS",
                "rates": rates,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # Fallback to mock data or raise error
            return {
                "status": "error",
                "message": str(e),
                "base": "UZS",
                "rates": {
                    "USD": 12500.00,
                    "EUR": 13600.00,
                    "RUB": 135.50
                },
                "timestamp": datetime.now().isoformat()
            }
