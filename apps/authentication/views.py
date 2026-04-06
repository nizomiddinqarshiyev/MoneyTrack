from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .serializers import RegisterSerializer, LoginSerializer, SendOTPSerializer, VerifyOTPSerializer
from .services import AuthService
from apps.wallets.services import WalletService
from apps.users.models import User

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: RegisterSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Automatically create default wallet
            WalletService.create_default_wallet(user)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "User registered successfully.",
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: LoginSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            
            # Check login attempts
            allowed, error_msg = AuthService.track_login_attempt(phone_number)
            if not allowed:
                return Response({"error": error_msg}, status=status.HTTP_403_FORBIDDEN)
            
            user = authenticate(username=phone_number, password=password)
            
            if user:
                AuthService.reset_login_attempts(phone_number)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=SendOTPSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code, error = AuthService.generate_otp(email)
            
            if error:
                return Response({"error": error}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                
            # In production, send Email here (e.g. via Celery task)
            from .tasks import send_otp_email
            send_otp_email.delay(email, code)
            print(f"DEBUG: OTP for {email} is {code}")
            
            return Response({"message": "OTP sent successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=VerifyOTPSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            success, message = AuthService.verify_otp(email, code)
            if success:
                return Response({"message": message})
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
