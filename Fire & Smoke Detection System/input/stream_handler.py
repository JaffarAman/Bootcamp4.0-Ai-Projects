import cv2

class StreamHandler:
    def __init__(self, source):
        self.source = source
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"Error: Could not open stream {source}")
            
    def read_frame(self):
        if not self.cap.isOpened():
            return False, None
        return self.cap.read()
        
    def release(self):
        self.cap.release()
