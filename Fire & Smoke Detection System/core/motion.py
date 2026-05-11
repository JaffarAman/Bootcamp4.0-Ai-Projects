import cv2

class MotionDetector:
    def __init__(self):
        # MOG2 background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=False)

    def get_motion_mask(self, blurred_frame):
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(blurred_frame)
        
        # Apply morphological operations to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        return fg_mask
