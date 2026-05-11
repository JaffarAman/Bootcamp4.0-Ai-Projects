# ✅ Yeh alag file hai — Streamlit is ko reset nahi karta
import threading

lock = threading.Lock()
buffer = []
