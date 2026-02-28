import cv2
import numpy as np
import urllib.request
import os
from dataclasses import dataclass

import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

_landmarker = None


def _get_landmarker():
    global _landmarker
    if _landmarker is None:
        if not os.path.exists(MODEL_PATH):
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
        )
        _landmarker = FaceLandmarker.create_from_options(options)
    return _landmarker


PITCH_MIN = 0.30   # en-dessous → caméra trop haute (regard vers le haut)
PITCH_MAX = 0.55   # au-dessus  → caméra trop basse (regard vers le bas)


@dataclass
class FacialRatios:
    eye_spacing_ratio: float
    nose_width_ratio: float
    nose_length_ratio: float
    mouth_width_ratio: float
    jaw_width_ratio: float
    face_length_ratio: float
    pitch_ratio: float


def extract_ratios(image_bytes: bytes) -> FacialRatios | None:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = _get_landmarker().detect(mp_img)
    if not result.face_landmarks:
        return None

    lm = result.face_landmarks[0]
    h, w = image.shape[:2]
    aspect = h / w  # corrige le fait que y est normalisé par h, x par w

    def dist_x(i, j):
        return abs(lm[j].x - lm[i].x)

    def dist_y(i, j):
        # Converti en "unités de largeur" pour être comparable à dist_x
        return abs(lm[j].y - lm[i].y) * aspect

    # Référence : coins externes des yeux (33=gauche, 263=droit)
    # Invariant au cadrage (selfie serré vs screenshot DD2 plan large)
    ocular_width = dist_x(33, 263)
    if ocular_width < 1e-6:
        return None

    eye_y   = (lm[133].y + lm[362].y) / 2
    face_h  = abs(lm[152].y - eye_y) * aspect
    nose_h  = abs(lm[4].y  - eye_y) * aspect
    pitch   = round(nose_h / face_h, 4) if face_h > 1e-6 else 0.0

    return FacialRatios(
        eye_spacing_ratio=round(dist_x(133, 362) / dist_x(129, 358), 4),
        nose_width_ratio=round(dist_x(129, 358) / ocular_width, 4),
        nose_length_ratio=round(dist_y(6, 4) / ocular_width, 4),
        mouth_width_ratio=round(dist_x(61, 291) / ocular_width, 4),
        jaw_width_ratio=round(dist_x(172, 397) / ocular_width, 4),
        face_length_ratio=round(dist_y(10, 152) / ocular_width, 4),
        pitch_ratio=pitch,
    )
