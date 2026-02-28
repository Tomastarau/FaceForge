import json
import os
import numpy as np
from ratio_calculator import FacialRatios

CALIBRATION_PATH = os.path.join(os.path.dirname(__file__), "calibration.json")

SLIDER_MIN = -100
SLIDER_MAX = 100

RATIO_FIELD = {
    "eye_spacing":  "eye_spacing_ratio",
    "nose_width":   "nose_width_ratio",
    "nose_length":  "nose_length_ratio",
    "mouth_width":  "mouth_width_ratio",
    "jaw_width":    "jaw_width_ratio",
    "face_length":  "face_length_ratio",
}

_calibration: dict | None = None


def _load_calibration() -> dict:
    global _calibration
    if _calibration is None:
        with open(CALIBRATION_PATH) as f:
            _calibration = json.load(f)
    return _calibration


def map_to_sliders(ratios: FacialRatios) -> dict:
    calibration = _load_calibration()
    result = {}

    for feature, field in RATIO_FIELD.items():
        if feature not in calibration:
            continue

        anchors = sorted(calibration[feature]["anchors"], key=lambda a: a["ratio"])
        xs = [a["ratio"] for a in anchors]
        ys = [a["slider"] for a in anchors]

        ratio_value = getattr(ratios, field)
        raw = float(np.interp(ratio_value, xs, ys))
        result[feature] = max(SLIDER_MIN, min(SLIDER_MAX, round(raw)))

    return result
