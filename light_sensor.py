import time
import board
from adafruit_veml7700 import VEML7700
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Firebase setup
cred = credentials.Certificate('/home/FredFukong/milestone1-41a80-firebase-adminsdk-511at-a5cbc28464.json')  # Path to the Firebase private key
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://milestone1-41a80-default-rtdb.firebaseio.com/'  # Your Realtime Database URL
})

# Create I2C bus
i2c = board.I2C()

# Initialize VEML7700 sensor
veml = VEML7700(i2c)

while True:
    lux = veml.lux
    print(f"Light Intensity: {lux:.2f} Lux")

    # Upload to Firebase
    ref = db.reference('gs://milestone1-41a80.appspot.com/vemldata')  # This path where data will be stored
    ref.push({
        'timestamp': time.time(),
        'lux': lux
    })

    time.sleep(5)  # Collect data every 5 seconds
