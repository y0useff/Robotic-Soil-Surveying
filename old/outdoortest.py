# ============ Cloud Setup ============ #
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from pynput import keyboard
import requests
import os
import certifi
import time

# SSL Cert fix for macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

# Replace with your credentials
CLIENT_ID = "AzOYta7zQjr5sGzfNHw9o1CiSzSJWPZm"
CLIENT_SECRET = "F6LiuiWfZuYKDARPfOZdKaZHySb7nERs5PVD2LqvzU7V4qOxrnl66c5x9wDiv2il"
THING_ID = "3c4a5f3c-7d78-4933-94a3-b74448082cad"
PROPERTY_ID = "0f36dfb8-dc59-4b16-bbcf-eedbe6ac1b85"

def get_access_token():
    try:
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
        return token.get("access_token")
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def send_command_to_cloud(command_str):
    access_token = get_access_token()
    url = f"https://api2.arduino.cc/iot/v2/things/{THING_ID}/properties/{PROPERTY_ID}/publish"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"value": command_str}
    
    try:
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Sent command to cloud: {command_str}")
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
        send_command_to_cloud("ON7")
        send_command_to_cloud("OFF8")
        print("Closed state commands sent")



# ============ Keyboard Listener Setup ============ #

def on_press(key):
    try:
        if key.char == 'o':  # open
            send_command_to_cloud("ON8")
            send_command_to_cloud("OFF7")
        elif key.char == 'c':  # close
            send_command_to_cloud("ON7")
            send_command_to_cloud("OFF8")
    except:
        send_command_to_cloud("ON7")
        send_command_to_cloud("OFF8")
            
print("Listening for key presses:")
print("  - Press 'o' to send ON8 OFF7 (open)")
print("  - Press 'c' to send ON7 OFF8 (close)")
print("  - Press 'esc' to exit")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
