from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(email, code):
    """
    Sends an Email with the OTP code using SMTP.
    """
    print(f"--- EMAIL GATEWAY ---")
    print(f"Sending OTP {code} to {email}...")
    
    subject = "Your OTP Code"
    message = f"Your Verification Code is: {code}\n\nThis code will expire in 5 minutes."
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"Email sent successfully to {email}.")
        return True
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
        return False
