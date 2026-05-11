# 🔥 Fire & Smoke Detection System

A real-time **Fire and Smoke Detection System** built using **Computer Vision**, **Machine Learning (YOLO)**, and **Python**, designed to detect fire and smoke from **live camera feeds**, **uploaded videos**, or **images**, and trigger **instant alerts** through alarms and email notifications.

---

# 📌 Project Overview

This project combines **traditional image processing techniques** (OpenCV) with **deep learning-based object detection** (YOLO) to create an intelligent safety monitoring system.

The system continuously monitors video input, detects possible fire regions using **color analysis** and **motion detection**, verifies them using a trained **YOLO model**, and then triggers alerts if fire is confirmed.

This makes the system suitable for:

* Homes
* Offices
* Warehouses
* Factories
* Smart surveillance systems
* Industrial safety monitoring

---

# 👨‍💻 Team Members

This was a **group project** completed by:

* **Abdul Moiz Muhammadi**
* **Mustafa Muktar**
* **Rehan**

---

# 🚀 Features

✅ Real-time fire detection using webcam
✅ Smoke detection using trained YOLO model
✅ Classical computer vision fire detection
✅ Motion-based filtering to reduce false alarms
✅ Alarm sound on fire detection
✅ Email notification with screenshot attachment
✅ Streamlit web interface
✅ FastAPI backend API
✅ Supports image, video, and live stream input
✅ Modular and scalable architecture

---

# 🛠 Technologies Used

## Programming Language

* Python 3.x

## Libraries

* OpenCV (`cv2`) – image/video processing
* NumPy – matrix operations
* Ultralytics YOLO – deep learning detection
* Streamlit – web UI
* FastAPI – REST API backend
* SMTP – email alerts
* Threading – background email sending
* Winsound – alarm sound (Windows)

---

# 📂 Project Structure

```text
fire/
│── app.py                 # Streamlit web application
│── api.py                 # FastAPI backend API
│── main.py                # Main desktop execution file
│── config.py              # Configuration settings
│── Smoke Fire.pt          # Trained YOLO model
│── alarm.wav              # Alarm audio
│
├── core/
│   ├── preprocessing.py   # Image preprocessing
│   ├── motion.py          # Motion detection
│   └── tracking.py        # Object tracking placeholder
│
├── detection/
│   ├── fire.py            # Fire detection logic
│   └── spark.py           # Spark detection
│
├── input/
│   └── stream_handler.py  # Camera/video input handling
│
├── logic/
│   └── decision.py        # Decision engine
│
├── output/
│   ├── alert.py           # Alarm + email alerts
│   └── display.py         # Display results
│
└── tests/
    └── evaluation.py      # Testing file
```

---

# ⚙️ System Workflow

```text
Camera / Video / Image
        ↓
Read Frame
        ↓
Preprocessing
(Resize + Blur + HSV + Gray)
        ↓
Motion Detection
        ↓
Classical Fire Detection
(Color Thresholding)
        ↓
YOLO Verification
        ↓
Decision Engine
        ↓
Alarm + Email Alert
        ↓
Display Final Output
```

---

# 🔍 Detailed Workflow Explanation

## 1. Input Acquisition

The system accepts input from:

* Live webcam (`STREAM_SOURCE = 0`)
* Video file
* Uploaded image

Handled by:

```python
cv2.VideoCapture()
```

---

## 2. Preprocessing

Implemented in: `core/preprocessing.py`

### Resize

```python
cv2.resize()
```

Purpose:

* Standardizes frame size
* Improves processing speed
* Reduces memory usage

Without resize:

* slower system
* lag in real-time detection

---

### Gaussian Blur

```python
cv2.GaussianBlur()
```

Purpose:

* removes image noise
* smooths frame
* prevents false fire detections

Without blur:

* random bright pixels may trigger false alarms

---

### HSV Conversion

```python
cv2.cvtColor(...HSV)
```

Purpose:

* easier color-based fire detection
* detects red/orange/yellow flames accurately

---

### Grayscale Conversion

```python
cv2.cvtColor(...GRAY)
```

Purpose:

* simplifies motion detection
* reduces computational cost

---

# 3. Motion Detection

Implemented in: `core/motion.py`

Uses:

```python
cv2.createBackgroundSubtractorMOG2()
```

Purpose:

* detects moving regions only
* filters static orange objects

Output:

* motion mask (white = motion)

---

# 4. Classical Fire Detection

Implemented in: `detection/fire.py`

### Fire Color Mask

```python
cv2.inRange()
```

Detects fire-colored pixels.

---

### Mask Combination

```python
cv2.bitwise_and()
```

Combines:

* motion mask
* fire color mask

Result:
Only moving fire remains.

---

### Morphological Operations

```python
cv2.erode()
cv2.dilate()
```

Purpose:

* remove tiny false positives
* connect broken fire regions

---

### Contour Detection

```python
cv2.findContours()
```

Finds fire boundaries.

Returns bounding boxes.

---

# 5. YOLO Verification

Implemented in:

```python
model(frame)
```

Purpose:

* confirms whether detected region is actually fire/smoke
* reduces false positives

Confidence threshold:

```python
0.20
```

---

# 6. Decision Engine

Implemented in: `logic/decision.py`

Logic:

* fire must appear in **5 consecutive frames**
* then trigger alarm

Purpose:

* avoids false alarms from brief flashes

---

# 7. Alert System

Implemented in: `output/alert.py`

Functions:

* plays alarm (`alarm.wav`)
* sends email notification
* attaches screenshot
* cooldown prevents email spam

---

# 8. Display Output

Implemented in: `output/display.py`

Uses:

```python
cv2.rectangle()
cv2.putText()
cv2.imshow()
```

Displays:

* red detection boxes
* “FIRE DETECTED” label

---

# ▶️ How to Run

## Install dependencies

```bash
pip install opencv-python numpy ultralytics streamlit fastapi uvicorn
```

---

## Run desktop app

```bash
python main.py
```

---

## Run Streamlit UI

```bash
streamlit run app.py
```

---

## Run FastAPI backend

```bash
uvicorn api:app --reload
```

---

# Future Improvements

* SMS alerts
* cloud deployment
* mobile app integration
* better smoke classification
* multi-camera support
* database logging

---

# Conclusion

This project demonstrates how **computer vision** and **deep learning** can be integrated to build a practical real-time fire safety system. By combining **classical image processing**, **motion analysis**, and **YOLO verification**, the system achieves better accuracy while reducing false alarms.

It is a scalable solution for real-world fire monitoring applications.

---

# Contributors

Developed by:
**Abdul Moiz Muhammadi**
**Mustafa Muktar**
**Rehan**
