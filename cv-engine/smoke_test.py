import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from src.config import LOGS_DIR, LOGS_FILE
    from src.proctoring.event_logger import event_logger
    from src.proctoring.face_tracker import FaceTracker
    from src.proctoring.phone_detector import PhoneDetector
    from src.proctoring.detector import ProctoringDetector
    
    print("Smoking Test: Imports successful.")
    
    # Test Event Logger
    event_logger.log_event("smoke_test", "low", {"status": "ok"})
    if os.path.exists(LOGS_FILE):
        print(f"Smoking Test: Log file created at {LOGS_FILE}")
    
    # Test Detector Initialization
    detector = ProctoringDetector()
    print("Smoking Test: Detector initialized successfully.")
    
    print("All smoke tests passed!")
except Exception as e:
    print(f"Smoke test failed: {e}")
    sys.exit(1)
