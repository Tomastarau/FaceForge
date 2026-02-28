import cv2
import numpy as np
import mediapipe as mp
import os
from mediapipe.tasks.python import vision, BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "face_landmarker.task")
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "IMG_8081.jpeg")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "landmarks_debug.jpg")

LANDMARKS = {
    133: ("eye_spacing L",  (0, 200, 255)),
    362: ("eye_spacing R",  (0, 200, 255)),
    129: ("nose_width L",   (0, 255, 100)),
    358: ("nose_width R",   (0, 255, 100)),
    61:  ("mouth L",        (255, 100, 0)),
    291: ("mouth R",        (255, 100, 0)),
    172: ("jaw L",          (200, 0, 255)),
    397: ("jaw R",          (200, 0, 255)),
    10:  ("face top",       (255, 220, 0)),
    152: ("chin",           (255, 220, 0)),
}

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.IMAGE,
    num_faces=1,
)
landmarker = FaceLandmarker.create_from_options(options)

img = cv2.imread(IMAGE_PATH)
h, w = img.shape[:2]
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
result = landmarker.detect(mp_img)

if not result.face_landmarks:
    print("Aucun visage détecté.")
    exit(1)

lm = result.face_landmarks[0]

radius    = max(4, min(w, h) // 150)
font_scale = max(0.4, min(w, h) / 1500)

for idx, (label, color) in LANDMARKS.items():
    x = int(lm[idx].x * w)
    y = int(lm[idx].y * h)
    cv2.circle(img, (x, y), radius, color, -1)
    cv2.putText(img, f"{idx}:{label}", (x + radius + 2, y + 4),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, max(1, radius // 3), cv2.LINE_AA)

cv2.imwrite(OUTPUT_PATH, img)
print(f"Image sauvegardée → {OUTPUT_PATH}")
