import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .services import FaceVerificationService
from .serializers import FaceEncodingSerializer, FaceVerificationResponseSerializer

class FaceRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FaceEncodingSerializer,
        responses={200: FaceVerificationResponseSerializer}
    )
    def post(self, request):
        """
        Registers a new face encoding for the user.
        Expects 'face_encoding' as a list of 128/512 floats.
        """
        encoding_list = request.data.get('face_encoding')
        if not encoding_list or not isinstance(encoding_list, list):
            return Response(
                {"status": "error", "message": "Invalid face encoding provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            encoding_np = np.array(encoding_list, dtype=np.float64)
            FaceVerificationService.register_face(request.user, encoding_np)
            
            # Update user's biometric status
            request.user.biometric_enabled = True
            request.user.save()
            
            return Response({"status": "success", "message": "Face registered successfully."})
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FaceVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FaceEncodingSerializer,
        responses={200: FaceVerificationResponseSerializer}
    )
    def post(self, request):
        """
        Verifies a face encoding against the stored profile.
        """
        encoding_list = request.data.get('face_encoding')
        if not encoding_list or not isinstance(encoding_list, list):
            return Response(
                {"status": "error", "message": "Invalid face encoding provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            encoding_np = np.array(encoding_list, dtype=np.float64)
            is_match = FaceVerificationService.verify_face(request.user, encoding_np)
            
            if is_match:
                return Response({"status": "success", "message": "Biometric verification successful."})
            else:
                return Response(
                    {"status": "error", "message": "Face did not match."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
