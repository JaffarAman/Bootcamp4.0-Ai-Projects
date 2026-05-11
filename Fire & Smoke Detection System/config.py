# config.py

import os

# Video Settings
STREAM_SOURCE = 0 # Webcam or file path
TARGET_SIZE = None # Use original resolution for CCTV to preserve long-range details (e.g. 1080p)
PROCESS_EVERY_N_FRAMES = 1

# Fire Detection Parameters (Classical)
FIRE_HSV_LOWER = (0, 100, 150)
FIRE_HSV_UPPER = (50, 255, 255)

# ML Integration
USE_ML = True
MODEL_PATH = "Smoke Fire.pt"
CONFIDENCE_THRESHOLD = 0.20  # Lowered for 15+ meter long range

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, MODEL_PATH)

# ── Email Alert Settings ──────────────────────────────────────────────────────
EMAIL_ENABLED       = True
SMTP_HOST           = "smtp.gmail.com"
SMTP_PORT           = 587                          # 587 = TLS (STARTTLS); use 465 for SSL
SMTP_USER           = "mohammadukkasha4@gmail.com"       # Sender Gmail address
SMTP_PASSWORD       = "ywxy rqym egov uhmf"     # Gmail App Password (NOT your login password)
EMAIL_RECIPIENT     = "abmoizs19@gmail.com"          # Where alerts are sent
EMAIL_SUBJECT       = "🔥 FIRE / SMOKE ALERT - Camera Detection"
EMAIL_COOLDOWN_SEC  = 60   # Minimum seconds between emails (avoids spam)