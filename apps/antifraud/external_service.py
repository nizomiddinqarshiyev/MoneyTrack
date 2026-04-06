import requests
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class ExternalAntifraudService:
    @staticmethod
    def check_transaction_risk(user, amount, transaction_type, wallet, receiver_wallet=None, ip_address=None, device_id=None):
        """
        Calls the external FastAPI Antifraud service to evaluate transaction risk.
        """
        # Determine the base URL (within Docker network)
        # In development outside docker, it might be localhost:8001
        base_url = getattr(settings, 'ANTIFRAUD_API_URL', 'http://antifraud-api:8000/api/v1')
        url = f"{base_url}/transactions/check"
        
        payload = {
            "transaction_id": f"tx_{timezone.now().timestamp()}", # Temporary ID for check
            "user_id": str(user.id),
            "sender_card": wallet.card_number if wallet else "unknown",
            "receiver_card": receiver_wallet.card_number if receiver_wallet else "unknown",
            "amount": float(amount),
            "currency": wallet.currency if wallet else "UZS",
            "timestamp": timezone.now().isoformat(),
            "sender_country": "UZ", # Default, could be derived from IP
            "receiver_country": "UZ",
            "ip_address": ip_address or "0.0.0.0",
            "device_id": device_id or "unknown",
            "channel": "MOBILE_APP"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Antifraud API error: {response.status_code} - {response.text}")
                # Fallback to approve if service is down but log it
                return {"decision": "APPROVED", "score": 0, "results": []}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Antifraud API: {str(e)}")
            # Fallback policy: allow transaction but log failure
            return {"decision": "APPROVED", "score": 0, "results": ["Service Unavailable"]}

    @staticmethod
    def start_biometric_session(transaction_id):
        """
        Starts a biometric session for a high-risk transaction.
        """
        base_url = getattr(settings, 'ANTIFRAUD_API_URL', 'http://antifraud-api:8000/api/v1')
        url = f"{base_url}/biometric/start-verification"
        
        try:
            response = requests.post(url, json={"transaction_id": transaction_id}, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to start biometric session: {str(e)}")
            return None
