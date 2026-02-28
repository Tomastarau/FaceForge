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

SLIDER_META = {
    "eye_spacing": {
        "label": "Écartement des yeux",
        "description": "Distance entre les coins internes des deux yeux, rapportée à la largeur totale entre coins externes. Un slider élevé signifie des yeux très espacés.",
    },
    "nose_width": {
        "label": "Largeur du nez",
        "description": "Largeur des ailes du nez rapportée à la largeur oculaire. Mesurée aux points les plus externes des narines.",
    },
    "nose_length": {
        "label": "Longueur du nez",
        "description": "Distance entre la racine du nez (entre les yeux) et sa pointe, normalisée par la largeur oculaire.",
    },
    "mouth_width": {
        "label": "Largeur de la bouche",
        "description": "Distance entre les deux commissures des lèvres, rapportée à la largeur oculaire.",
    },
    "jaw_width": {
        "label": "Largeur de la mâchoire",
        "description": "Largeur du bas du visage au niveau de la mâchoire, normalisée par la largeur oculaire. Reflète la carrure du visage.",
    },
    "face_length": {
        "label": "Hauteur du menton",
        "description": "Hauteur totale du visage du haut du front jusqu'au menton, normalisée par la largeur oculaire. Correspond au slider hauteur du menton dans DD2.",
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
