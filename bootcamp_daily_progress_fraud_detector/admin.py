import streamlit as st
import websocket
import threading
import json
import time
import os

st.set_page_config(page_title="Admin Panel", layout="wide")

QUEUE_FILE = "notification_queue.txt"
_file_lock = threading.Lock()


def write_message(msg: str):
    with _file_lock:
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


def read_and_clear_messages():
    with _file_lock:
        if not os.path.exists(QUEUE_FILE):
            return []
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            if lines:
                open(QUEUE_FILE, "w").close()  # clear
            return lines
        except:
            return []


# ── Session State Init ────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "shown_set" not in st.session_state:
    # ✅ Set: track karo kaunse messages toast ho chuke hain
    st.session_state.shown_set = set()

if "ws_started" not in st.session_state:
    st.session_state.ws_started = False


# ── WebSocket Handlers ────────────────────────────────
def on_message(ws, message):
    try:
        data = json.loads(message)
        msg = data.get("message", message)
        print("📨 WS Received:", msg)
        write_message(msg)  # file mein likho — UI main thread padh lega
    except Exception as e:
        print("Parse error:", e)


def on_error(ws, error):
    print("WS Error:", error)


def on_close(ws, code, msg):
    print("WS Closed")


def on_open(ws):
    print("WS Connected ✅")


def run_ws():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "ws://localhost:8000/ws",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open,
            )
            ws.run_forever()
        except Exception as e:
            print("WS crashed:", e)
        time.sleep(3)


if not st.session_state.ws_started:
    t = threading.Thread(target=run_ws, daemon=True)
    t.start()
    st.session_state.ws_started = True


# ── UI ────────────────────────────────────────────────
st.title("📢 Admin Notification Panel")

new_messages = read_and_clear_messages()

for msg in new_messages:
    # ✅ Sirf woh message show karo jo pehle nahi dikhaya
    if msg not in st.session_state.shown_set:
        st.session_state.shown_set.add(msg)
        st.session_state.messages.append(msg)
        st.toast(msg, icon="🔔")
        st.success(f"🔔 {msg}")
        print(f"✅ SHOWN: {msg}")

st.subheader("🔔 Notification History")

if st.session_state.messages:
    for m in reversed(st.session_state.messages[-10:]):
        st.info(f"🔔 {m}")
else:
    st.write("Abhi koi notification nahi aayi.")

time.sleep(1)
st.rerun()
