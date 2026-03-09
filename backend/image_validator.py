import cv2
import numpy as np
from dataclasses import dataclass
from ratio_calculator import FacialRatios, PITCH_MIN, PITCH_MAX

BLUR_WEIGHT = 40
LIGHTING_WEIGHT = 30
POSE_WEIGHT = 30
SCORE_THRESHOLD = 60

_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")


@dataclass
class GateResult:
    valid: bool
    message: str = ""
    gray: np.ndarray | None = None
    face_rect: tuple | None = None


MAX_DETECTION_SIZE = 1536
MAX_IMAGE_DIMENSION = 8000
MAX_IMAGE_PIXELS = 40_000_000

def validate_image(image_bytes: bytes) -> GateResult:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return GateResult(False, "Unable to decode the image.")

    h, w = image.shape[:2]
    if max(h, w) > MAX_IMAGE_DIMENSION or h * w > MAX_IMAGE_PIXELS:
        return GateResult(False, "Image dimensions too large.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape
    if max(h, w) > MAX_DETECTION_SIZE:
        scale = MAX_DETECTION_SIZE / max(h, w)
        detect_gray = cv2.resize(gray, (int(w * scale), int(h * scale)))
    else:
        scale = 1.0
        detect_gray = gray

    faces = _face_cascade.detectMultiScale(detect_gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        return GateResult(False, "No face detected in the image.")

    if len(faces) > 1:
        return GateResult(False, "Multiple faces detected. Please upload a photo with a single face.")

    x, y, fw, fh = faces[0]
    face_rect = (int(x / scale), int(y / scale), int(fw / scale), int(fh / scale))
    return GateResult(True, gray=gray, face_rect=face_rect)


BLUR_REJECT_THRESHOLD = 5

def score_quality(gray: np.ndarray, face_rect: tuple) -> tuple[int, str | None, str | None]:
    x, y, fw, fh = face_rect
    face_crop = gray[y:y + fh, x:x + fw]
    blur = _score_blur(face_crop)
    lighting = _score_lighting(gray)
    pose = _score_pose(gray, face_rect)
    score = int(blur + lighting + pose)

    if blur < BLUR_REJECT_THRESHOLD:
        return score, None, "Image too blurry to process. Please use a sharper photo."

    warning = (
        "Low quality image, results may be inaccurate. For best results: use a sharp, "
        "well-lit, front-facing photo with both eyes visible."
        if score < SCORE_THRESHOLD else None
    )
    return score, warning, None


def score_pitch(ratios: FacialRatios) -> str | None:
    if PITCH_MIN <= ratios.pitch_ratio <= PITCH_MAX:
        return None
    direction = "too high (look straight ahead)" if ratios.pitch_ratio < PITCH_MIN else "too low"
    return f"Camera angle {direction}, results may be less accurate."


def _score_blur(gray) -> float:
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    score = np.clip((variance - 30) / (200 - 30) * BLUR_WEIGHT, 0, BLUR_WEIGHT)
    return float(score)


def _score_lighting(gray) -> float:
    mean = gray.mean()
    if mean < 60:
        score = np.clip((mean - 40) / (60 - 40) * LIGHTING_WEIGHT, 0, LIGHTING_WEIGHT)
    elif mean > 200:
        score = np.clip((230 - mean) / (230 - 200) * LIGHTING_WEIGHT, 0, LIGHTING_WEIGHT)
    else:
        score = float(LIGHTING_WEIGHT)
    return float(score)


def _score_pose(gray, face_rect) -> float:
    x, y, w, h = face_rect
    face_roi = gray[y : y + h, x : x + w]
    eyes = _eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=5)

    if len(eyes) < 2:
        return POSE_WEIGHT * 0.3

    eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
    (cx1, cy1) = (eyes[0][0] + eyes[0][2] // 2, eyes[0][1] + eyes[0][3] // 2)
    (cx2, cy2) = (eyes[1][0] + eyes[1][2] // 2, eyes[1][1] + eyes[1][3] // 2)

    inter_eye = abs(cx1 - cx2) + 1e-6
    roll_offset = abs(cy1 - cy2) / inter_eye
    yaw_offset = abs((cx1 + cx2) / 2 - w / 2) / (w / 2 + 1e-6)

    yaw_penalty = float(np.clip(yaw_offset / 0.2, 0, 1))
    roll_penalty = float(np.clip(roll_offset / 0.15, 0, 1))

    score = POSE_WEIGHT * (1 - (yaw_penalty * 0.6 + roll_penalty * 0.4))
    return max(0.0, score)
