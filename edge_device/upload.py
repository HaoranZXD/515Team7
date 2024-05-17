import os
import subprocess
import json
from datetime import datetime
from time import sleep
from collections import deque
import board
import busio
from azure.storage.blob import BlobServiceClient
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_veml7700
from adafruit_bme280 import basic as adafruit_bme280

# Azure Blob Storage Setup
connect_str = 'Your connection string here'
container_name = 'Your container name here'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# Ensure the directory exists where photos and sensor data will be temporarily stored
photo_dir = 'Cloudphotos'
os.makedirs(photo_dir, exist_ok=True)

# Setup sensors
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)
veml7700 = adafruit_veml7700.VEML7700(i2c, address=0x10)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# Initialize a queue for SMA calculation of lux
window_size = 5  # Window size for the SMA
lux_queue = deque(maxlen=window_size)

def capture_photo():
    """Capture photo using libcamera-still and return the file path."""
    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(photo_dir, filename)
    cmd = ["libcamera-still", "-o", filepath]
    subprocess.run(cmd, check=True)
    print(f"Captured {filepath}")
    return filepath

def read_sensors():
    """Read sensor values, apply SMA on lux, and return them as a dictionary."""
    global lux_queue
    
    # Get current sensor readings
    current_lux = veml7700.lux
    lux_queue.append(current_lux)
    
    # Calculate SMA for lux
    avg_lux = sum(lux_queue) / len(lux_queue) if lux_queue else current_lux

    data = {
        'lux': avg_lux,
        'temperature': bme280.temperature,
        'humidity': bme280.humidity,
        'pressure': bme280.pressure,
        'uv_index': chan.voltage * 0.2  # Example conversion, adjust as necessary
    }
    print(f"Sensor Data with SMA for Lux: {data}")
    return data

def upload_to_azure(file_path, data, is_json=False):
    """Upload captured data to Azure Blob Storage."""
    blob_client = container_client.get_blob_client(blob=os.path.basename(file_path))
    if is_json:
        blob_client.upload_blob(json.dumps(data), overwrite=True)
    else:
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {file_path} to Azure Blob Storage")

def main():
    try:
        while True:
            # Read sensors and check UV index
            sensor_data = read_sensors()
            if sensor_data['uv_index'] > 0.1:
                # UV index is greater than 0, proceed with photo capture and upload
                photo_path = capture_photo()
                upload_to_azure(photo_path, None)
                
                sensor_filename = f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                sensor_filepath = os.path.join(photo_dir, sensor_filename)
                upload_to_azure(sensor_filepath, sensor_data, is_json=True)
                
                # Wait for 5 seconds before taking the next reading
                sleep(5)
            else:
                # UV index is 0 or less, skip this cycle and sleep
                print("UV index is 0 or less, skipping this cycle.")
                sleep(5)  # You can adjust the sleep time as needed
    except KeyboardInterrupt:
        print("Program interrupted")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
