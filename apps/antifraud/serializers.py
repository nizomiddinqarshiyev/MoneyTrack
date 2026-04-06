from rest_framework import serializers

class FaceEncodingSerializer(serializers.Serializer):
    face_encoding = serializers.ListField(
        child=serializers.FloatField(),
        min_length=128,
        help_text="A list of 128 or 512 floats representing the face encoding."
    )

class FaceVerificationResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
