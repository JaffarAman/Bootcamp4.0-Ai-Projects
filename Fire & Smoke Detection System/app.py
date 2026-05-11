import streamlit as st
import cv2
import tempfile
import numpy as np
import config

from core.preprocessing import preprocess_frame
from core.motion import MotionDetector
from core.tracking import RegionTracker
from detection.fire import get_fire_candidates_classical, verify_fire_ml
from logic.decision import DecisionEngine
from output.alert import AlertManager

st.title("🔥 Fire & Smoke Detection System")

# Sidebar
st.sidebar.header("Options")
mode = st.sidebar.selectbox("Select Mode", ["Live Camera", "Upload Video", "Upload Image"])
use_ml = st.sidebar.checkbox("Use ML Model", value=config.USE_ML)

# Load model
model = None
if use_ml:
    try:
        from ultralytics import YOLO
        model = YOLO(config.MODEL_FILE)
        st.sidebar.success("ML Model Loaded")
    except:
        st.sidebar.warning("ML model failed")

motion_det = MotionDetector()
decision_engine = DecisionEngine()
if "alert_mgr" not in st.session_state:
    st.session_state.alert_mgr = AlertManager()
alert_mgr = st.session_state.alert_mgr

if "silenced" not in st.session_state:
    st.session_state.silenced = False

def reset_alarm():
    st.session_state.silenced = False

# Sidebar - Alarm Control
st.sidebar.markdown("---")
st.sidebar.header("🚨 Alarm Control")

if st.session_state.silenced:
    st.sidebar.info("Alarm is currently MUTED")
    if st.sidebar.button("🔔 ENABLE ALARM", use_container_width=True):
        st.session_state.silenced = False
        st.rerun()
else:
    if alert_mgr.is_alarming:
        st.sidebar.warning("ALARM IS ACTIVE!")

    if st.sidebar.button("🛑 STOP ALARM", use_container_width=True):
        alert_mgr.acknowledge()
        st.session_state.silenced = True
        st.sidebar.success("Alarm Stopped & Muted")
        st.rerun()
st.sidebar.markdown("---")


# =========================
# 🔥 CORE FUNCTION
# =========================
def process_frame(frame):
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

        cv2.rectangle(resized, (x, y), (x+w, y+h), (0, 0, 255), 2)

    max_conf = max(confidences) if confidences else 0

    is_fire = len(boxes) > 0 or max_conf > 0.5

    return resized, is_fire, max_conf


# =========================
# 📸 IMAGE MODE
# =========================
if mode == "Upload Image":
    file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], on_change=reset_alarm)

    if file:
        img = np.asarray(bytearray(file.read()), dtype=np.uint8)
        frame = cv2.imdecode(img, 1)

        output, is_fire, conf = process_frame(frame)

        if is_fire:
            st.error(f"🔥 FIRE DETECTED ({conf*100:.1f}%)")
            if not alert_mgr.is_alarming and not st.session_state.silenced:
                alert_mgr.trigger("fire", frame=output)
        else:
            st.success(f"✅ NO FIRE ({conf*100:.1f}%)")

        st.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))


# =========================
# 🎥 VIDEO MODE
# =========================
elif mode == "Upload Video":
    file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"], on_change=reset_alarm)

    if file:
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(file.read())

        cap = cv2.VideoCapture(temp.name)
        frame_box = st.image([])

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            output, is_fire, conf = process_frame(frame)

            if is_fire:
                st.error(f"🔥 FIRE ({conf*100:.1f}%)")
                if not alert_mgr.is_alarming and not st.session_state.silenced:
                    alert_mgr.trigger("fire", frame=output)
            else:
                alert_mgr.acknowledge()

            frame_box.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

        cap.release()


# =========================
# 🎥 LIVE CAMERA
# =========================
elif mode == "Live Camera":
    start = st.button("Start")
    stop = st.button("Stop")

    if "run" not in st.session_state:
        st.session_state.run = False

    if start:
        st.session_state.run = True
        st.session_state.silenced = False
    if stop:
        st.session_state.run = False

    cap = cv2.VideoCapture(0)
    frame_box = st.image([])

    while st.session_state.run:
        ret, frame = cap.read()
        if not ret:
            break

        output, is_fire, conf = process_frame(frame)

        if is_fire:
            st.error(f"🔥 FIRE ({conf*100:.1f}%)")
            if not alert_mgr.is_alarming and not st.session_state.silenced:
                alert_mgr.trigger("fire", frame=output)
        else:
            alert_mgr.acknowledge()

        frame_box.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

    cap.release()