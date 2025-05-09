import os
import csv
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "logs", "detections.csv"))

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

if not os.path.exists(LOG_FILE):
  with open(LOG_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "species", "confidence"])

def log_prediction(species: str, confidence: float):
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  with open(LOG_FILE, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([timestamp, species, f"{confidence:.4f}"])