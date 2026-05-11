import time

class DecisionEngine:
    def __init__(self):
        self.fire_consecutive_frames = 0
        self.fire_trigger_frames = 5

    def evaluate(self, fire_candidates):
        is_fire = False
        
        # Fire logic: consistent detection over frames
        if len(fire_candidates) > 0:
            self.fire_consecutive_frames += 1
        else:
            self.fire_consecutive_frames = max(0, self.fire_consecutive_frames - 1)
            
        if self.fire_consecutive_frames >= self.fire_trigger_frames:
            is_fire = True
            
        return is_fire
