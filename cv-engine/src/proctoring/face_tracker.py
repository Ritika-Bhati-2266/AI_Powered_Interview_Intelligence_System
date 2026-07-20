import math
import time
from src.config import LOOK_AWAY_THRESHOLD, MOVEMENT_THRESHOLD, FRAME_WIDTH, FRAME_HEIGHT

class FaceTracker:
    def __init__(self):
        self.prev_center = None
        self.last_update_time = time.time()
        self.initial_center = None
        
    def update(self, face_rect):
        """
        Updates the tracker with current face rectangle (x, y, w, h).
        Returns a dictionary with movement analytics.
        """
        x, y, w, h = face_rect
        current_center = (x + w // 2, y + h // 2)
        
        # Initialize initial center for "looking away" detection
        if self.initial_center is None:
            self.initial_center = current_center
            
        movement_score = 0
        current_time = time.time()
        
        if self.prev_center:
            # Calculate Euclidean distance between frames
            dx = current_center[0] - self.prev_center[0]
            dy = current_center[1] - self.prev_center[1]
            movement_score = math.sqrt(dx**2 + dy**2)
            
        # Detect looking away (deviation from initial/steady center)
        # We normalize the deviation by frame width
        dev_x = abs(current_center[0] - self.initial_center[0]) / FRAME_WIDTH
        dev_y = abs(current_center[1] - self.initial_center[1]) / FRAME_HEIGHT
        looking_away = dev_x > LOOK_AWAY_THRESHOLD or dev_y > LOOK_AWAY_THRESHOLD
        
        # Determine if movement is stable or sudden
        stable = movement_score < MOVEMENT_THRESHOLD
        
        self.prev_center = current_center
        self.last_update_time = current_time
        
        return {
            "movement_score": round(movement_score, 2),
            "looking_away": looking_away,
            "stable": stable,
            "center": current_center
        }

    def reset_center(self):
        """Reset the 'stable' center position."""
        self.initial_center = self.prev_center
