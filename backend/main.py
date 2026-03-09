from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from image_validator import validate_image, score_quality, score_pitch
from ratio_calculator import extract_ratios
from slider_mapper import map_to_sliders

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/upload")
@limiter.limit("50/minute")
async def upload_image(request: Request, file: UploadFile = File(...)):
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10 MB.")

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

    return response
