import cv2

class DisplayManager:
    def __init__(self, window_name="Fire & Smoke Detection"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
    def draw(self, frame, fire_rects, is_fire):
        display_frame = frame.copy()
        
        # Draw fire bounding boxes
        for (x, y, w, h) in fire_rects:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(display_frame, "Fire", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
        # Draw Status text
        status_y = 30
        if is_fire: # Actually this is is_alarming now
            cv2.putText(display_frame, "!!! FIRE ALARM TRIGGERED !!!", (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(display_frame, "PRESS 'A' KEY TO STOP ALARM", (10, status_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
        cv2.imshow(self.window_name, display_frame)
        
    def stop(self):
        cv2.destroyAllWindows()
