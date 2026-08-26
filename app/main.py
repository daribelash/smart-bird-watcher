import os
import time
import cv2
import requests
import pandas as pd
from app.camera import Camera
from app.preprocess import preprocess_frame
from app.inference import BirdClassifier
from app.logger import log_prediction
from config.config import (
  TEXAS_BIRDS_CSV,
  MODEL_SAVE_PATH,
  STATIC_PATH,
  IMAGE_NAME,
  CONFIDENCE_THRESHOLD
)

def run_detection():
  class_names = sorted(pd.read_csv(TEXAS_BIRDS_CSV)["bird_name"].tolist())
  classifier = BirdClassifier(model_path=MODEL_SAVE_PATH, class_names=class_names)
  cam = Camera()

  try:
    while True:
      frame = cam.get_frame()
      input_tensor = preprocess_frame(frame)  # preprocesses the frame into a tensor for our model
      species, confidence = classifier.predict(input_tensor)  # prediction + its prob

      if confidence > CONFIDENCE_THRESHOLD:
        image_path = os.path.join(STATIC_PATH, IMAGE_NAME)
        cv2.imwrite(image_path, frame)
        log_prediction(species, confidence)

        # payload to fastapi (will implement later)
        payload = {
          "species": species,
          "confidence": confidence,
          "image_filename": IMAGE_NAME
        }
        try:
          # send POST request with metadata to fastapi
          res = requests.post("http://localhost:8000/predict", json=payload)
          # example output: [POST]{'species': 'Northern Cardinal', 'confidence': 0.9832, 'image_filename': 'latest.jpg'} -> Status: 200
          print(f"[POST]{payload} -> Status code: {res.status_code}")
        except Exception as e:
          print("Cannot send data (server is not running or network issue):", e)

        time.sleep(2)

  except KeyboardInterrupt:
    cam.release()
    print("\nStopping detection process.")