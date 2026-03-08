import json
import os
import numpy as np
from ratio_calculator import FacialRatios

CALIBRATION_PATH = os.path.join(os.path.dirname(__file__), "calibration.json")

SLIDER_MIN = -100
SLIDER_MAX = 100

RATIO_FIELD = {
    "eye_spacing":    "eye_spacing_ratio",
    "eye_size":       "eye_size_ratio",
    "nose_width":     "nose_width_ratio",
    "nose_length":    "nose_length_ratio",
    "mouth_width":    "mouth_width_ratio",
    "mouth_corner":   "mouth_corner_ratio",
    "jaw_width":      "jaw_width_ratio",
    "jaw_position":   "jaw_position_ratio",
    "chin_width":     "chin_width_ratio",
    "face_length":    "face_length_ratio",
    "brow_spacing":   "brow_spacing_ratio",
    "brow_height":    "brow_height_ratio",
    "brow_angle":     "brow_angle_ratio",
    "brow_curve":      "brow_curve_ratio",
    "lip_thickness":   "lip_thickness_ratio",
    "eye_tilt":        "eye_tilt_ratio",
    "eye_height":    "eye_height_ratio",
    "mouth_height":  "mouth_height_ratio",
}

SLIDER_META = {
    "eye_spacing": {
        "label": "Eye Spacing",
        "description": "Distance between the inner corners of both eyes relative to the total outer-to-outer width. A high value means widely spaced eyes.",
    },
    "eye_size": {
        "label": "Eye Size",
        "description": "Vertical opening of the eye between the upper and lower eyelid, normalized by eye width.",
    },
    "nose_width": {
        "label": "Nose Width",
        "description": "Width of the nostrils relative to eye width. Measured at the outermost points of the nose wings.",
    },
    "nose_length": {
        "label": "Nose Length",
        "description": "Distance from the nose bridge (between the eyes) to the tip, normalized by eye width.",
    },
    "mouth_width": {
        "label": "Mouth Width",
        "description": "Distance between the two mouth corners, relative to eye width.",
    },
    "mouth_corner": {
        "label": "Mouth Corner",
        "description": "Vertical position of the mouth corners relative to the lip center. Positive = corners lifted.",
    },
    "jaw_width": {
        "label": "Jaw Width",
        "description": "Width of the lower face at jaw level, normalized by eye width. Reflects overall face squareness.",
    },
    "jaw_position": {
        "label": "Jaw Position",
        "description": "Vertical distance between the mouth corners and the bottom of the jaw, normalized by eye width.",
    },
    "chin_width": {
        "label": "Chin Width",
        "description": "Width-to-height ratio of the chin — wide and square vs narrow and pointed.",
    },
    "face_length": {
        "label": "Face Length",
        "description": "Total face height from the top of the forehead to the chin, normalized by eye width. Maps to the chin height slider in DD2.",
    },
    "brow_spacing": {
        "label": "Brow Spacing",
        "description": "Distance between the inner corners of both eyebrows, normalized by eye width.",
    },
    "brow_height": {
        "label": "Brow Height",
        "description": "Vertical distance between the eye line and the eyebrows. Higher value means higher brows.",
    },
    "brow_angle": {
        "label": "Brow Angle",
        "description": "Slope of the eyebrow from inner to outer corner. Positive = outer corner higher (raised brow).",
    },
    "brow_curve": {
        "label": "Brow Curve",
        "description": "Height of the eyebrow arch above the line connecting its inner and outer corners.",
    },
    "lip_thickness": {
        "label": "Lip Thickness",
        "description": "Total vertical height of the lips from the upper edge to the lower edge, normalized by eye width.",
    },
    "eye_tilt": {
        "label": "Eye Tilt",
        "description": "Angle of the eye between inner and outer corners. Negative = outer corner higher (cat eyes). Positive = outer corner lower (drooping eyes).",
    },
    "eye_height": {
        "label": "Eye Height",
        "description": "Vertical position of the eyes on the face from the top of the skull, normalized by eye width.",
    },
    "mouth_height": {
        "label": "Mouth Height",
        "description": "Vertical position of the mouth on the face from the top of the skull, normalized by eye width.",
    },
}

_calibration: dict | None = None

def _load_calibration() -> dict:
    global _calibration
    if _calibration is None:
        with open(CALIBRATION_PATH) as f:
            _calibration = json.load(f)
    return _calibration

def map_to_sliders(ratios: FacialRatios) -> list[dict]:
    calibration = _load_calibration()
    result = []

    for feature, field in RATIO_FIELD.items():
        if feature not in calibration:
            continue

        anchors = sorted(calibration[feature]["anchors"], key=lambda a: a["ratio"])
        xs = [a["ratio"] for a in anchors]
        ys = [a["slider"] for a in anchors]

        ratio_value = getattr(ratios, field)
        raw = float(np.interp(ratio_value, xs, ys))
        value = max(SLIDER_MIN, min(SLIDER_MAX, round(raw)))
        meta = SLIDER_META[feature]
        result.append({
            "key": feature,
            "label": meta["label"],
            "description": meta["description"],
            "value": value,
        })

    return result
