import datetime
import time
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Path to your Firebase service account file
cred_path = '/home/FredFukong/milestone1-41a80-firebase-adminsdk-511at-a5cbc28464.json'

# Initialize the Firebase Admin with the service account
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'milestone1-41a80.appspot.com'
})

# Directory where photos will be saved
photo_dir = '/home/pi/CameraPhotos'
os.makedirs(photo_dir, exist_ok=True)

# Function to capture and upload photos
def capture_and_upload():
    while True:
        filename = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(photo_dir, filename)
        # Command to take a photo
        os.system(f'libcamera-still -o "{filepath}"')

        # Upload to Firebase
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        blob.upload_from_filename(filepath)

        # Wait for 10 seconds
        time.sleep(10)

if __name__ == '__main__':
    capture_and_upload()
