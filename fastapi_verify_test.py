import os
import requests
import random
import time

# Use the face_recognition library we installed
import face_recognition

def get_encoding(image_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return [random.uniform(-1, 1) for _ in range(128)]
    
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) > 0:
        return encodings[0].tolist()
    else:
        print(f"No face found in {image_path}. Using dummy.")
        return [random.uniform(-1, 1) for _ in range(128)]

# FastAPI Verify Endpoint (Port 8001)
url = "http://localhost:8001/api/v1/antifraud/verify"

# User ID from our previous tests (Django user ID 1 usually)
user_id = 1 

print(f"--- Testing FastAPI Face Verification on {url} ---")

# Test 1: Matching face (test_face.jpg)
print("\nTest 1: Same face (test_face.jpg)")
encoding1 = get_encoding("test_face.jpg")
payload1 = {"user_id": user_id, "face_encoding": encoding1}
response1 = requests.post(url, json=payload1)
print(f"Status Code: {response1.status_code}")
print(f"Response: {response1.json()}")

# Test 2: Different face (1.jpg)
print("\nTest 2: Different face (1.jpg)")
encoding2 = get_encoding("1.jpg")
payload2 = {"user_id": user_id, "face_encoding": encoding2}
response2 = requests.post(url, json=payload2)
print(f"Status Code: {response2.status_code}")
print(f"Response: {response2.json()}")
