from django.urls import path
from .views import FaceRegistrationView, FaceVerificationView

urlpatterns = [
    path('register/', FaceRegistrationView.as_view(), name='face-register'),
    path('verify/', FaceVerificationView.as_view(), name='face-verify'),
]
