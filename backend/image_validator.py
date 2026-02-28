import cv2
import numpy as np
from dataclasses import dataclass

BLUR_WEIGHT = 40
LIGHTING_WEIGHT = 30
POSE_WEIGHT = 30
SCORE_THRESHOLD = 60

_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")


@dataclass
class ValidationResult:
    score: int
    valid: bool
    message: str
    details: dict


def validate_image(image_bytes: bytes) -> ValidationResult:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return ValidationResult(0, False, "Impossible de décoder l'image.", {})

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

    if len(faces) == 0:
        return ValidationResult(0, False, "Aucun visage détecté dans l'image.", {})

    if len(faces) > 1:
        return ValidationResult(
            0,
            False,
            "Plusieurs visages détectés. Envoyez une photo avec un seul visage.",
            {},
        )

    blur_score = _score_blur(gray)
    lighting_score = _score_lighting(gray)
    pose_score = _score_pose(gray, faces[0])

    total = int(blur_score + lighting_score + pose_score)
    valid = total >= SCORE_THRESHOLD

    REJECTION_MESSAGE = (
        "Visage invalide. Le visage doit : être net et bien mis au point, "
        "avoir une exposition correcte (ni trop sombre ni surexposé), "
        "et être de face avec les deux yeux visibles."
    )

    if valid:
        message = "Image validée."
    else:
        message = REJECTION_MESSAGE

    return ValidationResult(
        score=total,
        valid=valid,
        message=message,
        details={
            "blur": round(blur_score, 1),
            "lighting": round(lighting_score, 1),
            "pose": round(pose_score, 1),
        },
    )


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
