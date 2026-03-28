"""
Face detection service using OpenCV Haar Cascade.
Accepts a raw image (bytes) and returns the number of faces detected.
"""
import cv2
import numpy as np


# Load cascade once at module level (avoids reloading on every request)
_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def count_faces(image_bytes: bytes) -> int:
    """
    Decode image bytes and count faces using Haar Cascade.
    Returns int: number of faces detected (0, 1, 2, ...)
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        return 0

    # Upscale small frames — improves detection on 320x240 webcam captures
    h, w = img.shape[:2]
    if w < 480:
        img = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LINEAR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)  # critical for webcam lighting

    faces = _cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,    # finer scale steps — catches more faces
        minNeighbors=2,      # very liberal — partial/half face counts
        minSize=(20, 20),    # very small minimum — catches far/partial faces
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    count = len(faces) if isinstance(faces, np.ndarray) else 0
    print(f"[FaceDetect] frame={w}x{h} detected={count}")

    # Liberal rule: >=1 detection = someone is present = ok
    # Only flag if truly 0 detections (completely hidden/absent)
    return count
