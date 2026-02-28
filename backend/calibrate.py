import json
import os
import sys
from ratio_calculator import extract_ratios

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "dogma character images")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "calibration.json")

# Pour chaque feature : liste de (fichier, valeur_slider_connue)
# Les images "par défaut" donnent une ancre intermédiaire fiable (slider != 0 en général)
ANCHORS = {
    "eye_spacing": [
        ("ecartement des yeux minimum.png", -100),
        ("ecartement des yeux maximum.png",  100),
    ],
    "nose_width": [
        ("taille et largeur narines minimum.png", -100),
        ("nez par défaut.png",                      0),   # Largeur des narines = 0 dans cette image
        ("taille et largeur narines max.png",       100),
    ],
    "nose_length": [
        ("longueur du nez minimum.png",  -100),
        ("nez par défaut.png",             16),   # Longueur du nez = 16 dans cette image
        ("longueur du nez maximum.png",   100),
    ],
    "mouth_width": [
        ("largeur de la bouche minimum.png",  -100),
        ("bouche par défaut.png",               14),   # Largeur de la bouche = 14 dans cette image
        ("largeur de la bouche maximum.png",   100),
    ],
    "jaw_width": [
        ("largeur de la machoire minimum.png",  -100),
        ("largeur de la machoire maximum.png",   100),
    ],
    "face_length": [
        ("hauteur du menton minimum.png",  -100),
        ("hauteur du menton maximum.png",   100),
    ],
}

RATIO_FIELD = {
    "eye_spacing":  "eye_spacing_ratio",
    "nose_width":   "nose_width_ratio",
    "nose_length":  "nose_length_ratio",
    "mouth_width":  "mouth_width_ratio",
    "jaw_width":    "jaw_width_ratio",
    "face_length":  "face_length_ratio",
}


def main():
    # Charger la calibration existante pour préserver eye_spacing
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            calibration = json.load(f)
        print(f"Calibration existante chargée ({len(calibration)} features préservées)\n")
    else:
        calibration = {}

    any_failure = False

    for feature, entries in ANCHORS.items():
        calibration[feature] = {"anchors": []}
        for filename, slider_value in entries:
            path = os.path.join(IMAGES_DIR, filename)
            with open(path, "rb") as f:
                image_bytes = f.read()

            ratios = extract_ratios(image_bytes)
            if ratios is None:
                print(f"[FAIL] Aucun visage détecté : {filename}")
                any_failure = True
                continue

            ratio_value = getattr(ratios, RATIO_FIELD[feature])
            calibration[feature]["anchors"].append({
                "ratio":  ratio_value,
                "slider": slider_value,
                "source": filename,
            })
            tag = "défaut" if "défaut" in filename else ("min" if slider_value == -100 else "max")
            print(f"[OK]  {feature:12s} | {tag:6s} | ratio={ratio_value:.4f}  slider={slider_value:+4d}  ({filename})")

        anchors = calibration[feature]["anchors"]
        if len(anchors) >= 2:
            delta = anchors[-1]["ratio"] - anchors[0]["ratio"]
            print(f"       → delta ratio min→max : {delta:+.4f}\n")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(calibration, f, indent=2, ensure_ascii=False)

    print(f"Calibration sauvegardée → {OUTPUT_PATH}")
    print(f"Features calibrées : {list(calibration.keys())}")

    if "eye_spacing" not in calibration:
        print("\n⚠️  eye_spacing manquant — capture 'écartement des yeux minimum.png' et 'écartement des yeux maximum.png' dans le jeu pour compléter la calibration.")

    if any_failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
