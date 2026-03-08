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

PITCH_MIN = 0.30
PITCH_MAX = 0.55

@dataclass
class FacialRatios:
    eye_spacing_ratio: float
    eye_size_ratio: float
    nose_width_ratio: float
    nose_length_ratio: float
    mouth_width_ratio: float
    mouth_corner_ratio: float
    jaw_width_ratio: float
    jaw_position_ratio: float
    chin_width_ratio: float
    face_length_ratio: float
    brow_spacing_ratio: float
    brow_height_ratio: float
    brow_angle_ratio: float
    brow_curve_ratio: float
    lip_thickness_ratio: float
    eye_tilt_ratio: float
    eye_height_ratio: float
    mouth_height_ratio: float
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
    aspect = h / w

    def dist_x(i, j):
        return abs(lm[j].x - lm[i].x)

    def dist_y(i, j):
        return abs(lm[j].y - lm[i].y) * aspect

    ocular_width = dist_x(33, 263)
    if ocular_width < 1e-6:
        return None

    eye_y   = (lm[133].y + lm[362].y) / 2
    face_h  = abs(lm[152].y - eye_y) * aspect
    nose_h  = abs(lm[4].y  - eye_y) * aspect
    pitch   = round(nose_h / face_h, 4) if face_h > 1e-6 else 0.0

    eye_size = (dist_y(159, 145) + dist_y(386, 374)) / 2

    mouth_corner = ((lm[13].y - lm[61].y) + (lm[13].y - lm[291].y)) / 2 * aspect

    jaw_position = (dist_y(61, 172) + dist_y(291, 397)) / 2

    chin_w = dist_x(149, 378)
    chin_h = (abs(lm[152].y - lm[149].y) + abs(lm[152].y - lm[378].y)) / 2 * aspect
    chin_width = chin_w / chin_h if chin_h > 1e-6 else 0.0

    brow_in_y = (lm[55].y + lm[285].y) / 2
    brow_height = (eye_y - brow_in_y) * aspect

    brow_spacing = dist_x(55, 285)

    angle_L = (lm[55].y - lm[46].y) * aspect
    angle_R = (lm[285].y - lm[276].y) * aspect
    brow_angle = (angle_L + angle_R) / 2

    def arch_height(in_idx, out_idx, top_idx):
        x_in,  y_in  = lm[in_idx].x,  lm[in_idx].y
        x_out, y_out = lm[out_idx].x, lm[out_idx].y
        x_top, y_top = lm[top_idx].x, lm[top_idx].y
        dx = x_out - x_in
        if abs(dx) < 1e-6:
            return 0.0
        t = (x_top - x_in) / dx
        y_line = y_in + t * (y_out - y_in)
        return (y_line - y_top) * aspect

    brow_curve = (arch_height(55, 46, 105) + arch_height(285, 276, 334)) / 2

    lip_thickness = dist_y(0, 17)

    tilt_L = (lm[33].y - lm[133].y) * aspect
    tilt_R = (lm[263].y - lm[362].y) * aspect
    eye_tilt = (tilt_L + tilt_R) / 2

    eye_height = (lm[152].y - eye_y) * aspect

    mouth_height = (lm[13].y - lm[10].y) * aspect

    return FacialRatios(
        eye_spacing_ratio=round(dist_x(133, 362) / dist_x(129, 358), 4),
        eye_size_ratio=round(eye_size / ocular_width, 4),
        nose_width_ratio=round(dist_x(129, 358) / ocular_width, 4),
        nose_length_ratio=round(dist_y(6, 4) / ocular_width, 4),
        mouth_width_ratio=round(dist_x(61, 291) / ocular_width, 4),
        mouth_corner_ratio=round(mouth_corner / ocular_width, 4),
        jaw_width_ratio=round(dist_x(172, 397) / ocular_width, 4),
        jaw_position_ratio=round(jaw_position / ocular_width, 4),
        chin_width_ratio=round(chin_width, 4),
        face_length_ratio=round(dist_y(10, 152) / ocular_width, 4),
        brow_spacing_ratio=round(brow_spacing / ocular_width, 4),
        brow_height_ratio=round(brow_height / ocular_width, 4),
        brow_angle_ratio=round(brow_angle / ocular_width, 4),
        brow_curve_ratio=round(brow_curve / ocular_width, 4),
        lip_thickness_ratio=round(lip_thickness / ocular_width, 4),
        eye_tilt_ratio=round(eye_tilt / ocular_width, 4),
        eye_height_ratio=round(eye_height / ocular_width, 4),
        mouth_height_ratio=round(mouth_height / ocular_width, 4),
        pitch_ratio=pitch,
    )
