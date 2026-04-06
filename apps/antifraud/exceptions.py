from rest_framework.exceptions import APIException
from rest_framework import status

class BiometricAuthRequired(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Biometric authentication is required for this transaction.'
    default_code = 'biometric_auth_required'

    def __init__(self, detail=None, code=None, reasons=None):
        super().__init__(detail, code)
        self.reasons = reasons or []

    def get_full_details(self):
        details = super().get_full_details()
        details['reasons'] = self.reasons
        return details
