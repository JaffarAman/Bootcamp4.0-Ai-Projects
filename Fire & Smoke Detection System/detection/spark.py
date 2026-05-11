import cv2
import numpy as np

class SparkDetector:
    def __init__(self, intensity_thresh=240):
        self.intensity_thresh = intensity_thresh
        self.prev_gray = None

    def detect(self, current_gray):
        candidates = []
        if self.prev_gray is not None:
            # Temporal differencing
            diff = cv2.absdiff(current_gray, self.prev_gray)
            
            # Intensity thresholding
            _, bright_mask = cv2.threshold(current_gray, self.intensity_thresh, 255, cv2.THRESH_BINARY)
            
            # Combine temporal and spatial
            spark_mask = cv2.bitwise_and(diff, bright_mask)
            
            # Find contours
            contours, _ = cv2.findContours(spark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for c in contours:
                area = cv2.contourArea(c)
                # Sparks are small
                if 1 < area < 50:
                    x, y, w, h = cv2.boundingRect(c)
                    candidates.append((x, y, w, h))

        self.prev_gray = current_gray
        return candidates
