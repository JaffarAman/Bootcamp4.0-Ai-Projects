import cv2
import config
from input.stream_handler import StreamHandler
from core.preprocessing import preprocess_frame
from core.motion import MotionDetector
from core.tracking import RegionTracker
from detection.fire import get_fire_candidates_classical, verify_fire_ml
from logic.decision import DecisionEngine
from output.alert import AlertManager
from output.display import DisplayManager

def main():
    print("Starting Fire & Smoke Detection System...")
    
    # Initialize components
    stream = StreamHandler(config.STREAM_SOURCE)
    motion_det = MotionDetector()
    tracker = RegionTracker()
    decision_engine = DecisionEngine()
    alert_mgr = AlertManager()
    display_mgr = DisplayManager()
    
    # Optional ML integration setup
    model = None
    if config.USE_ML:
        try:
            from ultralytics import YOLO
            model = YOLO(config.MODEL_FILE)
            print("ML Model loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load ML model: {e}. Falling back to classical.")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = stream.read_frame()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % config.PROCESS_EVERY_N_FRAMES != 0:
                continue
                
            # 1. Preprocess
            resized, blurred, hsv, gray = preprocess_frame(frame, config.TARGET_SIZE)
            
            # 2. Extract specific features (Motion, Color Candidate)
            fg_mask = motion_det.get_motion_mask(blurred)
            fire_candidates = get_fire_candidates_classical(hsv, config.FIRE_HSV_LOWER, config.FIRE_HSV_UPPER, fg_mask, config)
            
            # 3. Verify Fire
            verified_fire = verify_fire_ml(model, resized, fire_candidates, conf_thresh=config.CONFIDENCE_THRESHOLD)
            
            # 4. Make Decision
            is_fire = decision_engine.evaluate(verified_fire)
            
            # 5. Alarms
            if is_fire:
                alert_mgr.trigger("fire/smoke", frame=resized)
                
            # 6. Display
            display_mgr.draw(resized, verified_fire, alert_mgr.is_alarming)
            
            # Break loop on 'q' or Acknowledge on 'a'
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'): # 'a' key manually stops the alarm
                alert_mgr.acknowledge()
                
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        stream.release()
        display_mgr.stop()
        print("System shutdown complete.")

if __name__ == "__main__":
    main()