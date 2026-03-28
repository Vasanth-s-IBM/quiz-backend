"""
Proctoring route — receives a webcam frame and returns face count.
Also exposes the proctoring config for the exam page.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth.dependencies import get_current_user, require_role
from app.models.models import User
from app.services.face_detection import count_faces
from app.services.proctor_config import load_config

router = APIRouter()

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB


class FaceCheckResponse(BaseModel):
    face_count: int
    status: str      # "ok" | "no_face" | "multiple_faces"
    message: str


@router.get("/config")
def get_config(current_user: User = Depends(get_current_user)):
    """Return proctoring config — accessible by any authenticated user."""
    return load_config()


@router.post("/check-face", response_model=FaceCheckResponse)
async def check_face(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["User"]))
):
    """
    Accepts a JPEG/PNG webcam snapshot.
    Applies config rules (allow_multiple_faces, allow_no_face) before flagging.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG / PNG / WebP images are accepted"
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image too large (max 2 MB)"
        )

    config = load_config()
    face_count = count_faces(image_bytes)
    print(f"[Proctor] user={current_user.id} size={len(image_bytes)}B faces={face_count} config={config}")

    # Apply config rules
    if face_count == 0 and config["allow_no_face"]:
        face_count = 1  # treat as ok if admin allows no-face

    if face_count > 1 and config["allow_multiple_faces"]:
        face_count = 1  # treat as ok if admin allows multiple faces

    if face_count == 1:
        return FaceCheckResponse(face_count=face_count, status="ok", message="Face detected — all good.")
    elif face_count == 0:
        return FaceCheckResponse(face_count=face_count, status="no_face",
                                 message="No face detected. Please ensure your face is visible.")
    else:
        return FaceCheckResponse(face_count=face_count, status="multiple_faces",
                                 message=f"{face_count} faces detected. Only one person is allowed.")
