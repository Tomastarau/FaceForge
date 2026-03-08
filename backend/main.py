import json, os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from image_validator import validate_image, validate_pitch
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
    result = validate_image(contents)

    if not result.valid:
        return {
            "status": "rejected",
            "score": result.score,
            "message": result.message,
            "details": result.details,
        }

    ratios = extract_ratios(contents)
    if ratios is None:
        raise HTTPException(status_code=500, detail="Landmark extraction failed.")

    pitch = validate_pitch(ratios, result.score)
    if not pitch.valid:
        return {"status": "rejected", "score": pitch.score, "message": pitch.message, "details": pitch.details}

    sliders = map_to_sliders(ratios)

    response = {
        "status": "ok",
        "score": result.score,
        "message": result.message,
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
