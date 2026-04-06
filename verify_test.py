import os
import django
import json
import requests
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

def get_fresh_token(phone_number='+998912351954'):
    User = get_user_model()
    try:
        user = User.objects.get(phone_number=phone_number)
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    except User.DoesNotExist:
        print(f"User with phone {phone_number} not found.")
        return None

# 1. Prepare face encoding
try:
    import face_recognition
    image_path = "test_face.jpg"
    if os.path.exists(image_path):
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            face_encoding = encodings[0].tolist()
        else:
            print("No face found in image. Using dummy.")
            face_encoding = [random.uniform(-1, 1) for _ in range(128)]
    else:
        print(f"Image {image_path} not found. Using dummy.")
        face_encoding = [random.uniform(-1, 1) for _ in range(128)]
except ImportError:
    print("face_recognition not installed. Using dummy encoding.")
    face_encoding = [random.uniform(-1, 1) for _ in range(128)]

# 2. Get fresh token
token = get_fresh_token()
if not token:
    print("Could not get token. Exiting.")
    exit(1)

# 3. Send to backend
# Pointing to the VERIFY endpoint
url = "http://localhost:8000/api/antifraud/verify/"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {"face_encoding": face_encoding}
print("====================================")
print(face_encoding)
print("====================================")
print(f"Sending verification request to {url}...")
response = requests.post(url, headers=headers, json=payload)

print(f"Status Code: {response.status_code}")
try:
    print(response.json())
except Exception:
    print(response.text)
