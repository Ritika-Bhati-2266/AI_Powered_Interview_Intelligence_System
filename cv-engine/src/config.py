import os

# Webcam Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Thresholds
NO_FACE_SECONDS = 3.0
LOOK_AWAY_THRESHOLD = 0.15  # Distance from center relative to frame width
MOVEMENT_THRESHOLD = 50.0   # Pixel movement spike threshold
PHONE_CONTOUR_AREA = 2000   # Minimum area for phone approximation
WARNING_COOLDOWN_SECONDS = 5.0

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")
LOGS_FILE = os.path.join(LOGS_DIR, "proctoring_events.json")

# Haar Cascade Path (Default OpenCV)
import cv2
HAAR_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
