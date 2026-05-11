from fastapi import FastAPI, UploadFile, File
import numpy as np
import cv2
import tempfile

import config
from core.preprocessing import preprocess_frame
from core.motion import MotionDetector
from detection.fire import get_fire_candidates_classical, verify_fire_ml
from logic.decision import DecisionEngine

app = FastAPI(title="🔥 Fire Detection API")

motion_det = MotionDetector()
decision_engine = DecisionEngine()

model = None
if config.USE_ML:
    try:
        from ultralytics import YOLO
        model = YOLO(config.MODEL_FILE)
    except:
        model = None


def process(frame):

    resized, blurred, hsv, gray = preprocess_frame(frame, config.TARGET_SIZE)

    fg_mask = motion_det.get_motion_mask(blurred)

    fire_candidates = get_fire_candidates_classical(
        hsv,
        config.FIRE_HSV_LOWER,
        config.FIRE_HSV_UPPER,
        fg_mask,
        config
    )

    verified_fire = verify_fire_ml(
        model,
        resized,
        fire_candidates,
        conf_thresh=config.CONFIDENCE_THRESHOLD
    )

    if verified_fire is None:
        verified_fire = []

    boxes = []
    confidences = []

    for item in verified_fire:
        if len(item) == 5:
            x, y, w, h, conf = item
        else:
            x, y, w, h = item
            conf = 0.6

        boxes.append((x, y, w, h))
        confidences.append(conf)

    max_conf = max(confidences) if confidences else 0

    is_fire = len(boxes) > 0 or max_conf > 0.5

    return is_fire, max_conf, boxes


@app.post("/predict-image")
async def image(file: UploadFile = File(...)):

    data = await file.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), 1)

    is_fire, conf, _ = process(frame)

    return {"fire": is_fire, "confidence": conf}


@app.post("/predict-video")
async def video(file: UploadFile = File(...)):

    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(await file.read())

    cap = cv2.VideoCapture(temp.name)

    total, fire_count, max_conf = 0, 0, 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        is_fire, conf, _ = process(frame)

        total += 1
        if is_fire:
            fire_count += 1

        max_conf = max(max_conf, conf)

    cap.release()

    return {
        "fire": fire_count > 0,
        "ratio": fire_count / total if total else 0,
        "confidence": max_conf
    }


@app.post("/predict-frame")
async def frame(file: UploadFile = File(...)):

    data = await file.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), 1)

    is_fire, conf, boxes = process(frame)

    return {
        "fire": is_fire,
        "confidence": conf,
        "boxes": len(boxes)
    }