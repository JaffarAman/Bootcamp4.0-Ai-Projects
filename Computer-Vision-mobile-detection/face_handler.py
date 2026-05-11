import cv2
import os
import time
import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from deepface import DeepFace

dataset_path = "dataset_faces"
os.makedirs(dataset_path, exist_ok=True)

def send_face_email(name, emp_id, sender, password, receiver):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = '👤 Person Recognized'

        body = f"""
✅ PERSON RECOGNIZED

Name: {name}
Employee ID: {emp_id}
Time: {time.strftime("%Y-%m-%d %H:%M:%S")}

This person was just detected by the system.
"""
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", str(e))

def register_person(name, emp_id, cam_src=0):
    cap = cv2.VideoCapture(cam_src)
    st_frame = st.empty()
    status = st.empty()
    
    if not cap.isOpened():
        status.error("Camera open nahi ho raha! Please make sure 'Live Detection' mein camera STOP kiya hua hai, aur koi doosra app camera use nahi kar raha.")
        return
        
    person_dir = os.path.join(dataset_path, f"{name}_{emp_id}")
    os.makedirs(person_dir, exist_ok=True)
    
    count = 0
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    status.info("Recording video for exactly 10 seconds. Please look at the camera.")
    
    start_time = time.time()
    last_save_time = 0
    
    while cap.isOpened() and (time.time() - start_time) < 10:
        ret, frame = cap.read()
        if not ret: break
        
        current_time = time.time()
        display_frame = frame.copy()
        
        if current_time - last_save_time >= 1.0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Take the largest face
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                x, y, w, h = faces[0]
                count += 1
                face_img = frame[y:y+h, x:x+w]
                cv2.imwrite(os.path.join(person_dir, f"face_{count}.jpg"), face_img)
                last_save_time = current_time
                
        # Draw only text, no face bounding boxes
        remaining_time = max(0, 10 - int(time.time() - start_time))
        cv2.putText(display_frame, f"Recording: {remaining_time}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if current_time - last_save_time < 0.5 and count > 0:
            cv2.putText(display_frame, "📸 Captured!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        st_frame.image(frame_rgb, channels="RGB", use_container_width=True)
        
    cap.release()
    status.success(f"Registration complete for {name} ({emp_id})! {count} face images saved in 10 seconds.")
    
    # Clear all DeepFace cache files to force rebuild
    for f in os.listdir(dataset_path):
        if f.endswith(".pkl"):
            try:
                os.remove(os.path.join(dataset_path, f))
            except:
                pass

def run_live_face_recognition(cam_src, email_enabled, sender, password, receiver):
    cap = cv2.VideoCapture(cam_src)
    st_frame = st.empty()
    log_area = st.empty()
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    last_match_name = "Unknown"
    last_check_time = 0
    emails_sent = set()
    
    logs = []
    
    while cap.isOpened() and st.session_state.get('camera_active_face', False):
        ret, frame = cap.read()
        if not ret: break
        
        current_time = time.time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0 and (current_time - last_check_time) > 2.0:
            last_check_time = current_time
            
            # Check if there are any registered faces before running DeepFace
            if len(os.listdir(dataset_path)) > 0:
                try:
                    cv2.imwrite("temp_face.jpg", frame)
                    dfs = DeepFace.find(img_path="temp_face.jpg", db_path=dataset_path, enforce_detection=False, silent=True)
                    if len(dfs) > 0 and len(dfs[0]) > 0:
                        matched_path = dfs[0].iloc[0]['identity']
                        folder_name = matched_path.split(os.sep)[-2]
                        last_match_name = folder_name
                        
                        if email_enabled and last_match_name != "Unknown" and last_match_name not in emails_sent:
                            try:
                                name, emp_id = last_match_name.split('_')
                            except:
                                name, emp_id = last_match_name, "N/A"
                            send_face_email(name, emp_id, sender, password, receiver)
                            emails_sent.add(last_match_name)
                            logs.append(f"Email sent for {name} ({emp_id})")
                            
                    else:
                        last_match_name = "Unknown"
                except Exception as e:
                    last_match_name = "Unknown"
            else:
                last_match_name = "No Data"
                
        for (x,y,w,h) in faces:
            color = (0,255,0) if last_match_name != "Unknown" and last_match_name != "No Data" else (255,0,0)
            cv2.rectangle(frame, (x,y), (x+w, y+h), color, 2)
            cv2.putText(frame, last_match_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
        st_frame.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
        if logs:
            log_area.markdown("<br>".join(logs), unsafe_allow_html=True)
            
    cap.release()

def get_person_identity(frame):
    try:
        if not os.path.exists(dataset_path) or len(os.listdir(dataset_path)) == 0:
             return "Unknown", None
             
        # Use ArcFace with internal detection
        dfs = DeepFace.find(img_path=frame, db_path=dataset_path, model_name="ArcFace", distance_metric="cosine", enforce_detection=True, silent=True)
        
        if len(dfs) > 0 and len(dfs[0]) > 0:
             matched_path = dfs[0].iloc[0]['identity']
             dist = dfs[0].iloc[0]['distance']
             # Robust path splitting to get the folder name (Name_ID)
             folder_name = os.path.basename(os.path.dirname(matched_path))
             return folder_name, dist
        return "Unknown", None
    except Exception as e:
        if "Face could not be detected" not in str(e):
            print("DeepFace Error:", e)
        return "Unknown", None

def get_face_dirs():
    if not os.path.exists(dataset_path):
        return []
    return [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]

def parse_folder_name(folder_name):
    if "_" in folder_name:
        parts = folder_name.split("_")
        return parts[0], parts[1]
    return folder_name, "N/A"
