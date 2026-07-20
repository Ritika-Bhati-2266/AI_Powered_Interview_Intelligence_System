import cv2
import time
import sys
from src.config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from src.proctoring.detector import ProctoringDetector

def main():
    print("Starting AI Interview Proctoring System...")
    print("Press 'Q' to quit.")
    
    # Initialize Detector
    detector = ProctoringDetector()
    
    # Initialize Webcam
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    if not cap.isOpened():
        print(f"Error: Could not open webcam at index {CAMERA_INDEX}")
        sys.exit(1)
        
    prev_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Exiting.")
                break
                
            # Run Analysis
            analyzed_frame, stats = detector.analyze_frame(frame)
            
            # Calculate FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            
            # Display Stats on Frame
            cv2.putText(analyzed_frame, f"FPS: {round(fps, 1)}", (10, FRAME_HEIGHT - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(analyzed_frame, f"Faces: {stats['face_count']}", (10, FRAME_HEIGHT - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(analyzed_frame, f"Move Score: {stats['movement_score']}", (10, FRAME_HEIGHT - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Show Frame
            cv2.imshow("Proctoring Demo", analyzed_frame)
            
            # Handle Quitting
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Proctoring system shut down.")

if __name__ == "__main__":
    main()
