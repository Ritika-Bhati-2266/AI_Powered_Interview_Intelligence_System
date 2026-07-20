import cv2
import numpy as np
from src.config import PHONE_CONTOUR_AREA

class PhoneDetector:
    def __init__(self):
        pass
        
    def detect(self, frame, face_rect=None):
        """
        Detects rectangular objects that might be phones using contour detection.
        Focuses on the area around the face or lower frame.
        """
        # Convert to grayscale and blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny Edge Detection
        edged = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        phone_detected = False
        confidence = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < PHONE_CONTOUR_AREA:
                continue
                
            # Approximate the contour to a polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # If the polygon has 4 vertices, it's likely a rectangle
            if len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                
                # Phones usually have an aspect ratio between 1.5 and 2.5 (vertical or horizontal)
                if (0.4 < aspect_ratio < 0.7) or (1.4 < aspect_ratio < 2.5):
                    # Check if it's near the face region (if provided)
                    is_near_face = True
                    if face_rect:
                        fx, fy, fw, fh = face_rect
                        # Phone is usually held near mouth/ears or bottom of frame
                        # For simplicity, we just check if it's within a reasonable distance
                        dist_x = min(abs(x - fx), abs(x + w - (fx + fw)))
                        dist_y = min(abs(y - fy), abs(y + h - (fy + fh)))
                        if dist_x > fw * 1.5 or dist_y > fh * 1.5:
                            is_near_face = False
                    
                    if is_near_face:
                        phone_detected = True
                        confidence = min(int((area / (PHONE_CONTOUR_AREA * 5)) * 100), 100)
                        break
        
        return {
            "phone_detected": phone_detected,
            "confidence": confidence
        }
