Camera / Video / Image Input
        │
        ▼
Read Frame (cv2.VideoCapture)
        │
        ▼
Preprocessing
   ├── Resize
   ├── Blur (Noise Removal)
   ├── Convert to HSV
   └── Convert to Gray
        │
        ▼
Motion Detection
   ├── Background Subtraction
   ├── Create Motion Mask
   └── Clean Mask
        │
        ▼
Classical Fire Detection
   ├── Fire Color Mask
   ├── Merge with Motion Mask
   ├── Morphology (erode/dilate)
   └── Find Contours
        │
        ▼
ML Verification (YOLO)
   ├── Model predicts fire/smoke
   └── Confidence check
        │
        ▼
Decision Engine
   ├── Count consecutive fire frames
   └── Confirm fire
        │
        ▼
Alert System
   ├── Play alarm
   ├── Send email
   └── Save screenshot
        │
        ▼
Display Output
   ├── Draw boxes
   └── Show final result