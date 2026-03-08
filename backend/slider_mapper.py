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
        "label": "Écartement des yeux",
        "description": "Distance entre les coins internes des deux yeux, rapportée à la largeur totale entre coins externes. Un slider élevé signifie des yeux très espacés.",
    },
    "eye_size": {
        "label": "Taille des yeux",
        "description": "Ouverture verticale de l'œil entre la paupière supérieure et inférieure, normalisée par la largeur oculaire.",
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
    "mouth_corner": {
        "label": "Commissure des lèvres",
        "description": "Position verticale des coins de la bouche par rapport au centre des lèvres. Positif = coins relevés.",
    },
    "jaw_width": {
        "label": "Largeur de la mâchoire",
        "description": "Largeur du bas du visage au niveau de la mâchoire, normalisée par la largeur oculaire. Reflète la carrure du visage.",
    },
    "jaw_position": {
        "label": "Position de la mâchoire",
        "description": "Distance verticale entre les commissures et le bas de la mâchoire, normalisée par la largeur oculaire.",
    },
    "chin_width": {
        "label": "Largeur du menton",
        "description": "Rapport largeur/hauteur du menton — large et carré vs étroit et pointu. Calculé entre les points latéraux du menton et sa pointe.",
    },
    "face_length": {
        "label": "Hauteur du menton",
        "description": "Hauteur totale du visage du haut du front jusqu'au menton, normalisée par la largeur oculaire. Correspond au slider hauteur du menton dans DD2.",
    },
    "brow_spacing": {
        "label": "Écartement des sourcils",
        "description": "Distance entre les coins internes des deux sourcils, normalisée par la largeur oculaire.",
    },
    "brow_height": {
        "label": "Hauteur des sourcils",
        "description": "Distance verticale entre la ligne des yeux et les sourcils. Plus la valeur est élevée, plus les sourcils sont hauts.",
    },
    "brow_angle": {
        "label": "Angle des sourcils",
        "description": "Pente du sourcil entre son coin interne et son coin externe. Positif = coin externe plus haut (sourcil relevé).",
    },
    "brow_curve": {
        "label": "Courbure des sourcils",
        "description": "Hauteur de l'arche du sourcil au-dessus de la droite reliant son coin interne à son coin externe.",
    },
    "lip_thickness": {
        "label": "Épaisseur des lèvres",
        "description": "Hauteur verticale totale des lèvres (bord supérieur lèvre du haut → bord inférieur lèvre du bas), normalisée par la largeur oculaire.",
    },
    "eye_tilt": {
        "label": "Angle des yeux",
        "description": "Angle des yeux entre le coin interne et externe. Négatif = coin externe plus haut (yeux de chat). Positif = coin externe plus bas (yeux tombants).",
    },
    "eye_height": {
        "label": "Hauteur des yeux",
        "description": "Position verticale des yeux sur le visage, depuis le sommet du crâne, normalisée par la largeur oculaire.",
    },
    "mouth_height": {
        "label": "Hauteur de la bouche",
        "description": "Position verticale de la bouche sur le visage, depuis le sommet du crâne, normalisée par la largeur oculaire.",
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
