import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import cv2
import torch
import pygame
import requests
from datetime import datetime
import pytz
import time
import os

# ——— Settings ———
API_URL      = "http://127.0.0.1:5000/save_location"
TIMEZONE_STR = 'Asia/Kolkata'
SIREN_PATH   = 'siren.wav'

# ——— Check if siren file exists ———
if not os.path.exists(SIREN_PATH):
    print(f"Error: Siren file '{SIREN_PATH}' not found.")
    exit()

# ——— Initialize siren ———
pygame.mixer.init()
siren_sound = pygame.mixer.Sound(SIREN_PATH)

# ——— Load YOLOv5 model ———
try:
    model = torch.hub.load(
        'ultralytics/yolov5',
        'custom',
        path=r'C:\Users\disha\OneDrive\Desktop\fire_detection_project\yolov5\runs\train\custom_model22\weights\best.pt',
        force_reload=True
    )
except Exception as e:
    print("Error loading YOLOv5 model:", e)
    exit()

# ——— Start video capture ———
video1 = cv2.VideoCapture(0)
if not video1.isOpened():
    print("Error: Could not access the camera.")
    exit()

# ——— State ———
siren_started_at = None

# ——— Helper functions ———
def get_geo_location():
    try:
        info = requests.get('https://ipinfo.io/json', timeout=5).json()
        return {
            "city":   info.get("city",   "Unknown"),
            "region": info.get("region", "Unknown"),
            "loc":    info.get("loc",    "0,0")
        }
    except Exception as e:
        print("⚠️ Geo lookup failed:", e)
        return {"city": "Unknown", "region": "Unknown", "loc": "0,0"}

def send_location_to_server(city, region, loc, timestamp):
    payload = {
        "city":      city,
        "region":    region,
        "location":  loc,
        "timestamp": timestamp
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=5)
        print(f"→ POST {payload} -> {resp.status_code}", resp.text)
    except Exception as e:
        print("❌ Error sending location:", e)

def get_local_timestamp():
    tz = pytz.timezone(TIMEZONE_STR)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S")

# ——— Main loop ———
frame_id = 0
while True:
    ret, frame = video1.read()
    if not ret:
        print("Error: Could not read frame")
        break

    # Optional: Skip frames to reduce lag
    # if frame_id % 2 != 0:
    #     frame_id += 1
    #     continue

    results = model(frame)
    preds = results.pandas().xywh[0]
    fire_detected = any(
        (row['name'].lower() == "fire" and row['confidence'] > 0.7)
        for _, row in preds.iterrows()
    )

    # Play siren once per detection
    if fire_detected and siren_started_at is None:
        print("🔥 Fire detected!")
        siren_sound.play()
        siren_started_at = time.time()

        geo = get_geo_location()
        timestamp = get_local_timestamp()
        send_location_to_server(
            city=geo["city"],
            region=geo["region"],
            loc=geo["loc"],
            timestamp=timestamp
        )

    # Stop siren after 3 seconds
    if siren_started_at and (time.time() - siren_started_at) >= 3:
        siren_sound.stop()
        siren_started_at = None

    # Display annotated frame
    rendered_frame = results.render()[0]  # returns a list of one frame
    cv2.imshow("Fire Detection", rendered_frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    frame_id += 1

# ——— Cleanup ———
cv2.destroyAllWindows()
video1.release()  