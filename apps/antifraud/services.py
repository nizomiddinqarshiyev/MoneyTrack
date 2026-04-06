import numpy as np
import logging
from django.utils import timezone
from django.db.models import Avg, StdDev
from apps.transactions.models import Transaction
from .models import TransactionRisk, UserLocation, FaceProfile

logger = logging.getLogger(__name__)

class RiskAssessmentService:
    @staticmethod
    def is_outlier(user, amount_tiyin):
        """
        Check if the transaction amount is an outlier for the user.
        Uses Mean + 3 * Standard Deviation rule.
        """
        stats = Transaction.objects.filter(user=user).aggregate(
            avg_amount=Avg('amount'),
            std_amount=StdDev('amount')
        )
        
        avg = stats['avg_amount']
        std = stats['std_amount']
        
        if avg is None:
            # New user with no history, everything is potentially risky if high amount
            return amount_tiyin > 10000000 # > 100,000 UZS (example threshold for new users)
            
        if std is None or std == 0:
            # Only one transaction or all transactions same amount
            return amount_tiyin > avg * 1.5
            
        threshold = avg + (3 * std)
        return amount_tiyin > threshold

    @staticmethod
    def is_cross_border(user, country_code):
        """
        Check if the current transaction is from a new country.
        """
        if not country_code:
            return False # Assume local if no country info
            
        last_known_locations = UserLocation.objects.filter(user=user).values_list('country_code', flat=True)
        
        if not last_known_locations.exists():
            return False # First time recording location
            
        return country_code not in last_known_locations

    @classmethod
    def evaluate_transaction(cls, user, amount, transaction_type, category=None, country_code=None):
        """
        Evaluates risk factors before a transaction is created.
        """
        reasons = []
        risk_level = 'low'
        
        # 1. Outlier check
        if cls.is_outlier(user, amount):
            risk_level = 'medium'
            reasons.append("Transaction amount is significantly higher than usual.")
            
        # 2. Location check
        if country_code and cls.is_cross_border(user, country_code):
            risk_level = 'high'
            reasons.append(f"Transaction originating from a new country: {country_code}.")
        
        # Save risk assessment (linked to user/amount since transaction doesn't exist yet)
        risk, created = TransactionRisk.objects.get_or_create(
            user=user,
            amount=amount,
            is_verified=False,
            defaults={'risk_level': risk_level, 'reasons': reasons}
        )
        
        if not created:
            risk.risk_level = risk_level
            risk.reasons = reasons
            risk.save()
            
        return risk

class FaceVerificationService:
    @staticmethod
    def verify_face(user, face_encoding_sample):
        """
        Verifies a face encoding against the user's stored face profile.
        Simulates face_recognition.compare_faces logic.
        """
        try:
            profile = user.face_profile
            print(profile)
            stored_encoding = np.frombuffer(profile.face_encoding, dtype=np.float64)
            
            # Use distance threshold (e.g., 0.6)
            distance = np.linalg.norm(stored_encoding - face_encoding_sample)
            is_match = distance < 0.6
            
            debug_msg = f"VERIFY DEBUG: dist={distance}, match={is_match}, stored[:3]={stored_encoding[:3]}, sample[:3]={face_encoding_sample[:3]}"
            print(debug_msg)
            logger.info(debug_msg)
            
            if is_match:
                # Update any pending risk assessment
                pending_risk = TransactionRisk.objects.filter(transaction__user=user, is_verified=False).last()
                if pending_risk:
                    pending_risk.is_verified = True
                    pending_risk.verification_time = timezone.now()
                    pending_risk.save()
                    
            return is_match
        except FaceProfile.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Face verification error: {str(e)}")
            return False

    @staticmethod
    def register_face(user, face_encoding):
        """
        Registers or updates a user's face profile.
        """
        encoding_bytes = face_encoding.tobytes()
        profile, created = FaceProfile.objects.update_or_create(
            user=user,
            defaults={'face_encoding': encoding_bytes}
        )
        return profile
