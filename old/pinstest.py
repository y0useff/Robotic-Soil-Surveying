# ============ Cloud Setup ============ #
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import iot_api_client as iot
from iot_api_client.configuration import Configuration
from iot_api_client.rest import ApiException
from iot_api_client.models.property_value import PropertyValue

import os
import certifi
import serial
import serial.tools.list_ports
import time

# SSL Cert fix for macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

# Replace with your credentials
CLIENT_ID = "AzOYta7zQjr5sGzfNHw9o1CiSzSJWPZm"
CLIENT_SECRET = "F6LiuiWfZuYKDARPfOZdKaZHySb7nERs5PVD2LqvzU7V4qOxrnl66c5x9wDiv2il"
THING_ID = "3c4a5f3c-7d78-4933-94a3-b74448082cad"
PROPERTY_ID = "0f36dfb8-dc59-4b16-bbcf-eedbe6ac1b85"

# Get access token
oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
token_url = "https://api2.arduino.cc/iot/v1/clients/token"
oauth = OAuth2Session(client=oauth_client)
token = oauth.fetch_token(
    token_url=token_url,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    include_client_id=True,
    audience="https://api2.arduino.cc/iot",
)
access_token = token.get("access_token")

# Set up API client
config = Configuration(host="https://api2.arduino.cc/iot")
config.access_token = access_token
api_client = iot.ApiClient(config)
properties_api = iot.PropertiesV2Api(api_client)

# Cloud command sender
def send_command_to_cloud(command_str):
    try:
        value_object = PropertyValue(value=command_str)
        properties_api.properties_v2_publish(THING_ID, PROPERTY_ID, value_object)
        print(f"Sent command to cloud: {command_str}")
    except ApiException as e:
        print("Error sending command:", e)


# ============ Serial Setup ============ #
# serialInst = serial.Serial()
# ports = serial.tools.list_ports.comports()
# portsList = [str(p.device) for p in ports]

# # If only one port is available, use it
# if len(portsList) == 1:
#     portVar = portsList[0]
# else:
#     print("Available ports:")
#     for i, port in enumerate(portsList):
#         print(f"{i}: {port}")
#     idx = int(input("Select port index: "))
#     portVar = portsList[idx]

# serialInst.baudrate = 9600
# serialInst.port = portVar

# try:
#     serialInst.open()
#     print(f"Connected to {portVar}")
# except Exception as e:
#     print(f"Failed to open serial port {portVar}: {e}")
#     exit(1)

# ============ Communication ============ #
time.sleep(3)

# Initial toggle
send_command_to_cloud("ON7")
send_command_to_cloud("OFF8")

print("closed")
closed_time = time.time()
closed_duration = 10
# while time.time() - closed_time < closed_duration:
#     if serialInst.in_waiting > 0:
#         packet = serialInst.readline()
#         print(packet.decode('utf-8').rstrip('\n'))

# Turn on other relay
print("opens")
send_command_to_cloud("ON8")
send_command_to_cloud("OFF7")

start_time = time.time()
duration = 90

# while time.time() - start_time < duration:
#     if serialInst.in_waiting > 0:
#         packet = serialInst.readline()
#         print(packet.decode('utf-8').rstrip('\n'))

print("SHIT IS TURNT OFF")
send_command_to_cloud("ON7")
send_command_to_cloud("OFF8")

end_time = time.time()
end_duration = 10
# while time.time() - end_time < end_duration:
#     if serialInst.in_waiting > 0:
#         packet = serialInst.readline()
#         print(packet.decode('utf-8').rstrip('\n'))

time.sleep(13)
# serialInst.close()
print("Serial port closed.")
