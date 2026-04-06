import random
import time
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from apps.authentication.models import OTPCode, LoginAttempt
from apps.users.models import User

class AuthService:
    @staticmethod
    def generate_otp(email):
        """
        Generates a 6-digit OTP, stores it in Redis with a 5-minute expiry,
        and ensures a 60-second window before resending.
        """
        redis_key = f"otp_cooldown_{email}"
        if cache.get(redis_key):
            return None, "Please wait 60 seconds before requesting a new code."

        code = str(random.randint(100000, 999999))
        
        # Store in Redis for 5 minutes
        cache.set(f"otp_{email}", code, timeout=300)
        # Cooldown for 60 seconds
        cache.set(redis_key, True, timeout=60)
        
        # Save to DB for audit/requirement
        OTPCode.objects.create(
            email=email,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        return code, None

    @staticmethod
    def verify_otp(email, code):
        """
        Verifies the OTP and clears it from Redis upon successful verification.
        """
        redis_key = f"otp_{email}"
        stored_code = cache.get(redis_key)
        
        if not stored_code:
            return False, "OTP expired or not found."
        
        if stored_code != code:
            return False, "Invalid OTP code."
            
        # One-time usage: delete after verification
        cache.delete(redis_key)
        
        # Mark in DB as used
        otp_record = OTPCode.objects.filter(email=email, code=code, is_used=False).last()
        if otp_record:
            otp_record.is_used = True
            otp_record.save()
            
        return True, "Success"

    @staticmethod
    def track_login_attempt(phone_number):
        """
        Tracks failed login attempts and locks account if needed.
        5 attempts -> 10 minutes lock.
        """
        attempt, created = LoginAttempt.objects.get_or_create(phone_number=phone_number)
        
        if attempt.is_locked and attempt.locked_until > timezone.now():
            return False, f"Account locked. Try again after {attempt.locked_until}"
            
        attempt.attempts += 1
        attempt.last_attempt = timezone.now()
        
        if attempt.attempts >= 5:
            attempt.is_locked = True
            attempt.locked_until = timezone.now() + timedelta(minutes=10)
            attempt.save()
            return False, "Too many failed attempts. Account locked for 10 minutes."
            
        attempt.save()
        return True, None

    @staticmethod
    def reset_login_attempts(phone_number):
        """
        Resets login attempts after a successful login.
        """
        LoginAttempt.objects.filter(phone_number=phone_number).update(
            attempts=0, is_locked=False, locked_until=None
        )
