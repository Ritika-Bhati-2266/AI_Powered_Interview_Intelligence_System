import cv2
import time
from src.config import HAAR_CASCADE_PATH, NO_FACE_SECONDS, WARNING_COOLDOWN_SECONDS
from src.proctoring.event_logger import event_logger
from src.proctoring.face_tracker import FaceTracker
from src.proctoring.phone_detector import PhoneDetector

class ProctoringDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        self.tracker = FaceTracker()
        self.phone_detector = PhoneDetector()
        
        self.last_face_time = time.time()
        self.cooldowns = {}
        
    def _is_in_cooldown(self, event_type):
        now = time.time()
        if event_type in self.cooldowns:
            if now - self.cooldowns[event_type] < WARNING_COOLDOWN_SECONDS:
                return True
        self.cooldowns[event_type] = now
        return False

    def analyze_frame(self, frame):
        """
        Main analysis pipeline.
        Detects faces, updates tracker, checks phone, and logs events.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        face_count = len(faces)
        now = time.time()
        
        # 1. Multiple Faces Detection
        if face_count > 1:
            if not self._is_in_cooldown("multiple_faces"):
                event_logger.log_event("multiple_faces", "high", {"face_count": face_count})
        
        # 2. No Face Detection
        if face_count == 0:
            if now - self.last_face_time > NO_FACE_SECONDS:
                if not self._is_in_cooldown("no_face"):
                    event_logger.log_event("no_face", "medium", {"seconds_missing": round(now - self.last_face_time, 1)})
        else:
            self.last_face_time = now
            
        # 3 & 4. Tracking and Phone Detection (only if at least one face)
        movement_score = 0
        phone_info = {"phone_detected": False, "confidence": 0}
        
        if face_count > 0:
            # We take the largest face for tracking
            main_face = max(faces, key=lambda f: f[2] * f[3])
            tracker_info = self.tracker.update(main_face)
            movement_score = tracker_info["movement_score"]
            
            # Sudden Movement
            if not tracker_info["stable"]:
                if not self._is_in_cooldown("sudden_movement"):
                    event_logger.log_event("sudden_movement", "low", {"movement_score": movement_score})
            
            # Looking Away
            if tracker_info["looking_away"]:
                if not self._is_in_cooldown("looking_away"):
                    event_logger.log_event("looking_away", "medium", {"movement_score": movement_score})
            
            # 5. Phone Detection
            phone_info = self.phone_detector.detect(frame, main_face)
            if phone_info["phone_detected"]:
                if not self._is_in_cooldown("phone_detected"):
                    event_logger.log_event("phone_detected", "high", {"confidence": phone_info["confidence"]})
            
            # Draw on frame
            self._draw_overlay(frame, faces, tracker_info, phone_info)
            
        return frame, {
            "face_count": face_count,
            "movement_score": movement_score,
            "phone_detected": phone_info["phone_detected"]
        }

    def _draw_overlay(self, frame, faces, tracker_info, phone_info):
        # Draw faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
        # Visual cues for tracking
        if tracker_info:
            center = tracker_info["center"]
            cv2.circle(frame, center, 5, (0, 255, 0), -1)
            if tracker_info["looking_away"]:
                cv2.putText(frame, "LOOKING AWAY!", (center[0]-50, center[1]-20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Phone Warning
        if phone_info["phone_detected"]:
            cv2.putText(frame, f"PHONE DETECTED! ({phone_info['confidence']}%)", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
