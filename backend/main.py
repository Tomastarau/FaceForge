import json, os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from image_validator import validate_image, score_quality, score_pitch
from ratio_calculator import extract_ratios
from slider_mapper import map_to_sliders

RESULT_PATH = os.path.join(os.path.dirname(__file__), "last_result.json")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()

    gate = validate_image(contents)
    if not gate.valid:
        return {"status": "rejected", "score": 0, "message": gate.message, "details": {}}

    ratios = extract_ratios(contents)
    if ratios is None:
        raise HTTPException(status_code=500, detail="Landmark extraction failed.")

    score, quality_warning, rejection = score_quality(gate.gray, gate.face_rect)
    if rejection:
        return {"status": "rejected", "score": score, "message": rejection, "details": {}}

    pitch_warning = score_pitch(ratios)
    warning = pitch_warning or quality_warning
    sliders = map_to_sliders(ratios)

    response = {
        "status": "ok",
        "score": score,
        "message": warning or "Image accepted.",
        "sliders": sliders,
        "ratios": {
            "eye_spacing_ratio": ratios.eye_spacing_ratio,
            "nose_width_ratio": ratios.nose_width_ratio,
            "mouth_width_ratio": ratios.mouth_width_ratio,
            "jaw_width_ratio": ratios.jaw_width_ratio,
            "face_length_ratio": ratios.face_length_ratio,
        },
    }

    with open(RESULT_PATH, "w") as f:
        json.dump(response, f, indent=2)

    return response
