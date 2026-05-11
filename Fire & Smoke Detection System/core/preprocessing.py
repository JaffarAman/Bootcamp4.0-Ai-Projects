import cv2

def preprocess_frame(frame, target_size=None):
    # Resize
    if target_size is not None:
        frame = cv2.resize(frame, target_size)
    
    # Blur to reduce noise
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    
    # Convert color spaces
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    
    return frame, blurred, hsv, gray
