import cv2
import numpy as np

def get_fire_candidates_classical(hsv_frame, hsv_lower, hsv_upper, fg_mask, config):
    # Mask by HSV color constraints
    color_mask = cv2.inRange(hsv_frame, np.array(hsv_lower), np.array(hsv_upper))
    
    # Combine color and motion to remove static bright objects
    if fg_mask is not None:
        mask = cv2.bitwise_and(color_mask, fg_mask)
    else:
        mask = color_mask
    
    # morphological operations
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > 10: # Lowered threshold further for max CCTV range
            x, y, w, h = cv2.boundingRect(c)
            candidates.append((x, y, w, h))
            
    return candidates

def check_overlap(boxA, boxB):
    x1_A, y1_A, w_A, h_A = boxA
    x1_B, y1_B, w_B, h_B = boxB
    xA = max(x1_A, x1_B)
    yA = max(y1_A, y1_B)
    xB = min(x1_A + w_A, x1_B + w_B)
    yB = min(y1_A + h_A, y1_B + h_B)
    return max(0, xB - xA) * max(0, yB - yA) > 0

def verify_fire_ml(model, frame, candidates, conf_thresh=0.20):
    if model is None:
        return candidates # fallback to classical if no model
        
    verified = []
    
    # Use YOLO model directly on the frame
    results = model(frame, verbose=False)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            if conf >= conf_thresh:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1
                ml_box = (x1, y1, w, h)
                
                # Check if ML bounding box overlaps with any classical candidate
                # We will keep the CLASSICAL box (c_box) because it is tightly fitted 
                # to the actual glowing/moving pixels, preventing huge bounding boxes.
                for c_box in candidates:
                    if check_overlap(ml_box, c_box):
                        if c_box not in verified:
                            verified.append(c_box)
                
    return verified
