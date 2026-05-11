import streamlit as st
import cv2
import time
import os
import numpy as np
import smtplib
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from ultralytics import YOLO
import threading
import concurrent.futures

# Global variables for Face Recognition
face_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
GLOBAL_IDENTITIES = []
GLOBAL_IDENTITY_OBJ = {"name": "Unknown", "display": "Unknown", "id": "N/A"}

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Distraction Detection Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px 0;
    }
    .metric-value { font-size: 36px; font-weight: 700; color: #ffffff; }
    .metric-label { font-size: 13px; color: #8892a4; margin-top: 5px; }
    .identity-card {
        background: linear-gradient(135deg, #1a1d35, #1e2245);
        border: 1px solid #4466ff;
        border-radius: 10px;
        padding: 14px; margin: 8px 0;
        text-align: center;
    }
    .identity-name { font-size: 22px; font-weight: 700; color: #66aaff; }
    .identity-id   { font-size: 14px; color: #8892a4; margin-top: 4px; }
    .status-distracted {
        background: linear-gradient(90deg, #ff4444, #cc0000);
        color: white; padding: 15px 25px; border-radius: 10px;
        text-align: center; font-size: 22px; font-weight: 700;
    }
    .status-normal {
        background: linear-gradient(90deg, #00cc44, #009933);
        color: white; padding: 15px 25px; border-radius: 10px;
        text-align: center; font-size: 22px; font-weight: 700;
    }
    .status-table {
        background: linear-gradient(90deg, #ffaa00, #cc8800);
        color: white; padding: 15px 25px; border-radius: 10px;
        text-align: center; font-size: 22px; font-weight: 700;
    }
    .sidebar-header { font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 10px; }
    .log-entry {
        background: #1a1d2e; border-left: 3px solid #ff4444;
        padding: 10px 15px; margin: 5px 0;
        border-radius: 0 8px 8px 0; font-size: 13px;
    }
    footer { display: none !important; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INIT
# ============================================
defaults = {
    'alert_log':       [],
    'email_log':       [],
    'total_alerts':    0,
    'total_emails':    0,
    'detection_start': None,
    'last_seen':       None,
    'alert_triggered': False,
    'camera_active':   False,
    'camera_active_face': False,
    'identity_obj':    {"name": "Unknown", "display": "Unknown", "id": "N/A"},
    'identities':      [],
    'last_ident_time': 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

os.makedirs('screenshots', exist_ok=True)

# ============================================
# LOAD MODELS
# ============================================
@st.cache_resource
def load_models():
    pose  = YOLO('yolo11n-pose.pt')
    phone = YOLO('yolo11n.pt')
    return pose, phone

pose_model, phone_model = load_models()

MOBILE      = 67
LEFT_WRIST  = 9
RIGHT_WRIST = 10

# ============================================
# SMTP EMAIL
# ============================================
def send_email(screenshot_path, elapsed, sender, password, receiver, person_name="Unknown"):
    try:
        msg            = MIMEMultipart()
        msg['From']    = sender
        msg['To']      = receiver
        msg['Subject'] = '🚨 Distraction Alert!'
        body = f"""
🚨 DISTRACTION ALERT!

📅 Time      : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
⏱ Duration  : {int(elapsed)} seconds
📱 Status   : Person using mobile detected
👤 Person   : {person_name}

Screenshot attached.
-- Distraction Detection Dashboard
        """
        msg.attach(MIMEText(body, 'plain'))
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment',
                           filename=os.path.basename(screenshot_path))
            msg.attach(img)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent!"
    except Exception as e:
        return False, str(e)

# ============================================
# DETECTION HELPERS
# ============================================
def get_center(box):
    return ((box[0]+box[2])/2, (box[1]+box[3])/2)

def distance(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def draw_box(frame, box, label, color):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1-25), (x1+w, y1), color, -1)
    cv2.putText(frame, label, (x1, y1-8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

def run_detection(frame, conf_thresh, wrist_dist):
    pose_res  = list(pose_model(frame, conf=conf_thresh,      stream=True, imgsz=320))[0]
    phone_res = list(phone_model(frame, conf=conf_thresh-0.1, iou=0.3, stream=True, imgsz=320))[0]

    phones, wrists = [], []

    for box in phone_res.boxes:
        if int(box.cls) == MOBILE:
            bbox = box.xyxy[0].tolist()
            conf = float(box.conf)
            phones.append({'box': bbox, 'conf': conf})
            draw_box(frame, bbox, f"Phone {conf:.2f}", (255,165,0))

    if pose_res.keypoints is not None:
        for kps in pose_res.keypoints.xy:
            for idx in [LEFT_WRIST, RIGHT_WRIST]:
                kp = kps[idx]
                x, y = float(kp[0]), float(kp[1])
                if x > 0 and y > 0:
                    wrists.append((x, y))
                    cv2.circle(frame, (int(x), int(y)), 8, (0,255,255), -1)

    # ── Person box + face identity (async via ThreadPool) ──
    now = time.time()
    if now - st.session_state.last_ident_time > 1.0:
        st.session_state.last_ident_time = now
        crops_data = []
        for box in pose_res.boxes:
            b = box.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, b)
            # Pass the full person box, face_handler.py will locate the face using CascadeClassifier
            crop = frame[max(0, y1):y2, max(0, x1):x2]
            if crop.size > 0:
                crops_data.append((b, crop.copy()))
        
        if crops_data:
            def update_all_identities(crops_list):
                try:
                    from face_handler import get_person_identity, parse_folder_name
                    new_identities = []
                    for b_box, p_crop in crops_list:
                        res = get_person_identity(p_crop)
                        if isinstance(res, tuple):
                            folder, score = res
                        else:
                            folder, score = res, None

                        if folder and folder not in ("Unknown", "No Data"):
                            p_name, p_id = parse_folder_name(folder)
                            new_identities.append({"box": b_box, "display": p_name, "id": p_id, "name": folder, "score": score})
                        else:
                            new_identities.append({"box": b_box, "display": "Unknown Person", "id": "N/A", "name": "Unknown", "score": None})
                    
                    global GLOBAL_IDENTITIES, GLOBAL_IDENTITY_OBJ
                    GLOBAL_IDENTITIES = new_identities
                    if new_identities:
                        GLOBAL_IDENTITY_OBJ = new_identities[0]
                except Exception as e:
                    print("Error in update_all_identities:", e)
            
            face_executor.submit(update_all_identities, crops_data)

    for box in pose_res.boxes:
        bbox = box.xyxy[0].tolist()
        
        # Match current box to known identities
        disp = "Unknown Person"
        eid = "N/A"
        score = None
        best_dist = float('inf')
        bc = get_center(bbox)
        
        for ident in GLOBAL_IDENTITIES:
            ic = get_center(ident['box'])
            d = distance(bc, ic)
            if d < best_dist and d < 300: # distance threshold to match boxes
                best_dist = d
                disp = ident.get('display', 'Unknown Person')
                eid = ident.get('id', 'N/A')
                score = ident.get('score', None)
                
        x1, y1, x2, y2 = map(int, bbox)
        if disp in ("Unknown", "Unknown Person"):
            color = (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            cv2.rectangle(frame, (x1, max(0, y1-40)), (x1+280, y1), color, -1)
            cv2.putText(frame, "Unknown Person", (x1+5, max(15, y1-10)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,255,255), 2)
        else:
            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            cv2.rectangle(frame, (x1, max(0, y1-75)), (x1+350, y1), color, -1)
            cv2.putText(frame, disp.upper(), (x1+5, max(30, y1-40)), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0,0,0), 3)
            conf_val = max(0, 100 - int((score or 0) * 100))
            score_txt = f" | Conf: {conf_val}%" if score is not None else ""
            cv2.putText(frame, f"ID: {eid}{score_txt}", (x1+5, max(15, y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)

    # ── Phone-in-use ──
    mobile_in_use = False
    for phone in phones:
        pc = get_center(phone['box'])
        for wrist in wrists:
            if distance(pc, wrist) < wrist_dist:
                mobile_in_use = True
                cv2.line(frame,
                         (int(wrist[0]), int(wrist[1])),
                         (int(pc[0]),    int(pc[1])),
                         (0, 0, 255), 2)
                draw_box(frame, phone['box'], "IN USE!", (0, 0, 255))

    return frame, mobile_in_use, len(phones), len(wrists) // 2

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.subheader("🎯 Detection")
    conf_thresh = st.slider("Confidence",       0.1, 0.9, 0.5, 0.05)
    wrist_dist  = st.slider("Wrist Distance",    50, 300, 150,   10)
    alert_time  = st.slider("Alert Time (sec)", 10,  300, 120,   10)
    tolerance   = st.slider("Tolerance (sec)",   1,   30,   7,    1)
    st.divider()
    st.subheader("📧 Email Config")
    email_enabled  = st.toggle("Enable Email Alerts", value=False)
    email_sender   = st.text_input("Sender Email",   placeholder="your@gmail.com")
    email_password = st.text_input("App Password",   type="password")
    email_receiver = st.text_input("Receiver Email", placeholder="receiver@gmail.com")
    st.divider()
    if st.button("🗑️ Clear All Logs", type="secondary"):
        st.session_state.alert_log    = []
        st.session_state.email_log    = []
        st.session_state.total_alerts = 0
        st.session_state.total_emails = 0
        st.rerun()

# ============================================
# MAIN DASHBOARD
# ============================================
st.title("🚨 Distraction Detection Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📹 Live Detection", "📊 Statistics",
    "🖼️ Alert History", "📧 Email Logs", "👤 Face Registration"
])

# ============================================
# TAB 1 — LIVE DETECTION  ← face name+ID shown here
# ============================================
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📹 Camera Feed")
        cam_source = st.text_input("Camera Source", value="0", help="0=webcam, or RTSP URL")
        c1, c2     = st.columns(2)
        start_btn  = c1.button("▶ Start Detection", type="primary",  use_container_width=True)
        stop_btn   = c2.button("⏹ Stop",            type="secondary", use_container_width=True)
        frame_placeholder  = st.empty()
        status_placeholder = st.empty()
        timer_placeholder  = st.empty()

    with col2:
        st.subheader("👤 Detected Person")
        identity_card = st.empty()   # name + ID card lives here
        st.divider()
        st.subheader("📊 Live Stats")
        m1 = st.empty(); m2 = st.empty(); m3 = st.empty(); m4 = st.empty()
        st.divider()
        st.subheader("📋 Live Log")
        log_placeholder = st.empty()

    if start_btn:
        st.session_state.camera_active   = True
        st.session_state.detection_start = None
        st.session_state.last_seen       = None
        st.session_state.alert_triggered = False
        GLOBAL_IDENTITY_OBJ    = {"name": "Unknown", "display": "Unknown", "id": "N/A"}
        GLOBAL_IDENTITIES      = []

    if stop_btn:
        st.session_state.camera_active = False
        if 'cap_obj' in st.session_state and st.session_state.cap_obj is not None:
            st.session_state.cap_obj.release()
            st.session_state.cap_obj = None
        st.rerun()                          # ← loop ko forcefully exit karo

    if st.session_state.camera_active:
        src = int(cam_source) if cam_source.isdigit() else cam_source
        
        if 'cap_obj' in st.session_state and st.session_state.cap_obj is not None:
            st.session_state.cap_obj.release()
            
        cap = cv2.VideoCapture(src)
        st.session_state.cap_obj = cap
        
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)

        fps_counter = 0; fps_display = 0; fps_time = time.time()

        try:
            while st.session_state.camera_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("Camera not accessible!")
                    break
    
                frame = cv2.resize(frame, (640, 480))
                frame, mobile_in_use, phone_count, person_count = run_detection(
                    frame, conf_thresh, wrist_dist)
    
                now = time.time()
    
                # ── Identity card update ──
                disp = str(GLOBAL_IDENTITY_OBJ.get("display", "Unknown"))
                eid  = str(GLOBAL_IDENTITY_OBJ.get("id",      "—"))
                identity_card.markdown(f"""
                <div class="identity-card">
                    <div class="identity-name">👤 {disp}</div>
                    <div class="identity-id">🪪 ID: {eid}</div>
                </div>""", unsafe_allow_html=True)
    
                # ── Distraction timer logic ──
                if mobile_in_use:
                    st.session_state.last_seen = now
                    if st.session_state.detection_start is None:
                        st.session_state.detection_start = now
                        st.session_state.alert_triggered = False
                        st.session_state.alert_log.append({
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'event': 'Detection Started', 'duration': 0, 'person': disp
                        })
                else:
                    if st.session_state.last_seen and (now - st.session_state.last_seen) > tolerance:
                        st.session_state.detection_start = None
                        st.session_state.last_seen       = None
                        st.session_state.alert_triggered = False
    
                if st.session_state.detection_start and not st.session_state.alert_triggered:
                    elapsed   = now - st.session_state.detection_start
                    remaining = alert_time - elapsed
    
                    if elapsed >= alert_time:
                        st.session_state.alert_triggered = True
                        st.session_state.total_alerts   += 1
                        filename = f"screenshots/alert_{int(now)}.jpg"
                        cv2.imwrite(filename, frame)
                        st.session_state.alert_log.append({
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'event': '🚨 ALERT TRIGGERED',
                            'duration': int(elapsed), 'person': disp, 'file': filename
                        })
                        if email_enabled and email_sender and email_password and email_receiver:
                            ok, msg = send_email(filename, elapsed,
                                                 email_sender, email_password,
                                                 email_receiver, disp)
                            st.session_state.email_log.append({
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'to': email_receiver, 'person': disp,
                                'status': '✅ Sent' if ok else f'❌ {msg}',
                                'file': os.path.basename(filename)
                            })
                            if ok: st.session_state.total_emails += 1
                        st.session_state.detection_start = None
                        st.session_state.last_seen       = None
    
                    mins = int(remaining) // 60; secs = int(remaining) % 60
                    cv2.rectangle(frame, (0, 0), (frame.shape[1], 55), (0, 0, 200), -1)
                    cv2.putText(frame, f"DISTRACTED! Alert in: {mins:02d}:{secs:02d}",
                                (15, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 3)
                    progress = min(elapsed / alert_time, 1.0)
                    cv2.rectangle(frame, (0, frame.shape[0]-15),
                                  (int(frame.shape[1]*progress), frame.shape[0]), (0,0,255), -1)
                    status_placeholder.markdown(
                        '<div class="status-distracted">🚨 DISTRACTED!</div>', unsafe_allow_html=True)
                    timer_placeholder.progress(progress, text=f"Alert in {mins:02d}:{secs:02d}")
    
                elif not mobile_in_use and phone_count > 0:
                    cv2.rectangle(frame, (0,0), (frame.shape[1], 55), (0,200,200), -1)
                    cv2.putText(frame, "Phone on TABLE", (15, 38),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
                    status_placeholder.markdown(
                        '<div class="status-table">📱 Phone on Table — OK</div>', unsafe_allow_html=True)
                    timer_placeholder.empty()
                else:
                    cv2.rectangle(frame, (0,0), (frame.shape[1], 55), (0,150,0), -1)
                    cv2.putText(frame, "Normal", (15, 38),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
                    status_placeholder.markdown(
                        '<div class="status-normal">✅ Normal</div>', unsafe_allow_html=True)
                    timer_placeholder.empty()
    
                fps_counter += 1
                if time.time() - fps_time >= 1.0:
                    fps_display = fps_counter; fps_counter = 0; fps_time = time.time()
                cv2.putText(frame, f"FPS: {fps_display}", (frame.shape[1]-120, 38),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
    
                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                                        channels="RGB", use_container_width=True)
                m1.markdown(f'<div class="metric-card"><div class="metric-value">{person_count}</div><div class="metric-label">👤 Persons</div></div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="metric-card"><div class="metric-value">{phone_count}</div><div class="metric-label">📱 Phones</div></div>', unsafe_allow_html=True)
                m3.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.total_alerts}</div><div class="metric-label">🚨 Total Alerts</div></div>', unsafe_allow_html=True)
                m4.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.total_emails}</div><div class="metric-label">📧 Emails Sent</div></div>', unsafe_allow_html=True)
    
                if st.session_state.alert_log:
                    log_html = "".join(
                        f'<div class="log-entry">⏰ {e["time"]} — {e["event"]} {"| "+str(e.get("person","")) if e.get("person") else ""}</div>'
                        for e in st.session_state.alert_log[-5:][::-1]
                    )
                    log_placeholder.markdown(log_html, unsafe_allow_html=True)

        finally:
            if 'cap_obj' in st.session_state and st.session_state.cap_obj is not None:
                st.session_state.cap_obj.release()
                st.session_state.cap_obj = None

# ============================================
# TAB 2 — STATISTICS
# ============================================
with tab2:
    st.subheader("📊 Detection Statistics")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.total_alerts}</div><div class="metric-label">🚨 Total Alerts</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.total_emails}</div><div class="metric-label">📧 Emails Sent</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div class="metric-value">{len(os.listdir("screenshots"))}</div><div class="metric-label">📸 Screenshots</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.alert_log)}</div><div class="metric-label">📋 Log Entries</div></div>', unsafe_allow_html=True)
    st.divider()
    if st.session_state.alert_log:
        df = pd.DataFrame(st.session_state.alert_log)
        col1, col2 = st.columns(2)
        with col1:
            events = df['event'].value_counts().reset_index()
            fig = px.pie(events, values='count', names='event', title='Event Distribution',
                         color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            alerts_only = df[df['event'] == '🚨 ALERT TRIGGERED']
            if not alerts_only.empty:
                fig2 = px.bar(alerts_only, x='time', y='duration', title='Alert Duration (seconds)',
                              color='duration', color_continuous_scale='Reds')
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data yet — start detection first!")

# ============================================
# TAB 3 — ALERT HISTORY
# ============================================
with tab3:
    st.subheader("🖼️ Alert Screenshots")
    screenshots = sorted([f for f in os.listdir('screenshots') if f.endswith('.jpg')], reverse=True)
    if screenshots:
        for i in range(0, len(screenshots), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i+j < len(screenshots):
                    fname = screenshots[i+j]
                    fpath = os.path.join('screenshots', fname)
                    with col:
                        st.image(Image.open(fpath), caption=fname, use_container_width=True)
                        ts = fname.replace('alert_','').replace('.jpg','')
                        try:
                            st.caption(f"📅 {datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')}")
                        except: pass
                        with open(fpath, 'rb') as f:
                            col.download_button("⬇️ Download", f.read(), fname, "image/jpeg",
                                                use_container_width=True)
    else:
        st.info("No screenshots yet.")

# ============================================
# TAB 4 — EMAIL LOGS
# ============================================
with tab4:
    st.subheader("📧 Email Logs")
    if st.session_state.email_log:
        df_email = pd.DataFrame(st.session_state.email_log)
        st.dataframe(df_email, use_container_width=True, column_config={
            'time': 'Time', 'to': 'Sent To', 'person': 'Person',
            'status': 'Status', 'file': 'Screenshot'
        })
        sent   = len([e for e in st.session_state.email_log if '✅' in e['status']])
        failed = len([e for e in st.session_state.email_log if '❌' in e['status']])
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#00cc44">{sent}</div><div class="metric-label">✅ Sent</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff4444">{failed}</div><div class="metric-label">❌ Failed</div></div>', unsafe_allow_html=True)
    else:
        st.info("No emails sent yet.")

# ============================================
# TAB 5 — FACE REGISTRATION
# ============================================
with tab5:
    st.subheader("👤 Register New Person")
    st.write("Register a person so they appear by name in **Live Detection** (Tab 1).")
    reg_name = st.text_input("Full Name",           placeholder="e.g. Ahmed")
    reg_id   = st.text_input("Employee / Person ID", placeholder="e.g. 101")
    cam_reg  = st.text_input("Camera Source", value="0", key="cam_reg")

    if st.button("📸 Start Registration (10 seconds)"):
        if reg_name and reg_id:
            from face_handler import register_person
            src = int(cam_reg) if cam_reg.isdigit() else cam_reg
            register_person(reg_name, reg_id, src)
        else:
            st.warning("Enter Name and ID first.")

    st.divider()
    st.subheader("👥 Registered Persons")
    from face_handler import get_face_dirs
    dirs = get_face_dirs()
    if dirs:
        for d in dirs:
            st.markdown(
                f"<span style='background:#0d3b2e;color:#00ff88;border:1px solid #00ff88;"
                f"border-radius:20px;padding:3px 14px;font-size:13px;margin:3px;"
                f"display:inline-block'>✓ {d}</span>", unsafe_allow_html=True)
    else:
        st.info("No persons registered yet.")

    if st.button("🗑️ Clear All Face Data", type="secondary"):
        import shutil
        from face_handler import dataset_path as dp
        shutil.rmtree(dp)
        os.makedirs(dp, exist_ok=True)
        st.success("All face data cleared.")