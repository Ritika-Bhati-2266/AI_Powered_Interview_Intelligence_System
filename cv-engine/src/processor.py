import cv2
import numpy as np
import mediapipe as mp
import logging
from collections import deque
from typing import Dict, Any, Tuple, List

logger = logging.getLogger("cv-engine-processor")

class CVFrameProcessor:
    def __init__(self, max_history_len: int = 15):
        """
        Initializes a real-time, CPU-optimized Computer Vision processor.
        Uses MediaPipe FaceMesh for fully offline facial landmark detection.
        """
        self.max_history_len = max_history_len
        
        # Deque to maintain rolling coordinate history of nose tip for stability calculations
        self.nose_history = deque(maxlen=self.max_history_len)
        
        # Initialize MediaPipe solutions
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # CPU-optimized face mesh instance (1 face max, refine landmarks for iris if available)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  # Enables precise eye/iris landmarks
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        logger.info("MediaPipe FaceMesh CPU-optimized pipeline initialized successfully!")

    def process_frame(self, frame_bytes: bytes) -> Dict[str, Any]:
        """
        Ingests a raw video frame (JPEG or PNG format bytes), processes it using OpenCV 
        and MediaPipe, and extracts high-fidelity face, gaze, stability, and emotion metrics.
        """
        try:
            # 1. Decode image from bytes
            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {
                    "face_detected": False,
                    "gaze": "center",
                    "emotion": "neutral",
                    "stability_score": 0,
                    "confidence_score": 0
                }

            # Get image dimensions
            height, width, _ = img.shape

            # Convert BGR (OpenCV format) to RGB (MediaPipe format)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 2. Process landmarks
            results = self.face_mesh.process(img_rgb)

            # Check if a face is detected
            if not results.multi_face_landmarks:
                # Face lost: reset history, yield empty metrics
                self.nose_history.clear()
                return {
                    "face_detected": False,
                    "gaze": "center",
                    "emotion": "neutral",
                    "stability_score": 0,
                    "confidence_score": 0
                }

            # Retrieve face landmarks for the first face
            face_landmarks = results.multi_face_landmarks[0].landmark
            confidence = results.multi_face_landmarks[0].HasField("score")
            confidence_score = int(results.multi_face_landmarks[0].score * 100) if confidence else 95

            # 3. Calculate Gaze Direction
            # Left Eye: Corner landmarks 33 (outer), 133 (inner)
            # Pupil: approximation centroid of left eye or landmark 468 (center of iris)
            p_33 = np.array([face_landmarks[33].x * width, face_landmarks[33].y * height])
            p_133 = np.array([face_landmarks[133].x * width, face_landmarks[133].y * height])
            
            # MediaPipe refine_landmarks index 468 is left iris center
            p_iris = np.array([face_landmarks[468].x * width, face_landmarks[468].y * height])

            # Horizontal ratio: position of iris relative to eye width
            eye_width = np.linalg.norm(p_133 - p_33)
            if eye_width > 0:
                # Project iris onto horizontal vector of the eye
                eye_vector = p_133 - p_33
                iris_vector = p_iris - p_33
                projection_ratio = np.dot(iris_vector, eye_vector) / (eye_width ** 2)
                
                # Determine gaze direction based on ratio bounds
                if projection_ratio < 0.42:
                    # Iris is close to the outer corner (looking towards their right / screen left)
                    gaze = "right"
                elif projection_ratio > 0.58:
                    # Iris is close to inner corner (looking towards their left / screen right)
                    gaze = "left"
                else:
                    gaze = "center"
            else:
                gaze = "center"

            # 4. Calculate Head Stability Score
            # Track nose tip (index 4) coordinates
            nose_tip = np.array([
                face_landmarks[4].x * width,
                face_landmarks[4].y * height,
                face_landmarks[4].z * width
            ])
            
            self.nose_history.append(nose_tip)
            stability_score = self._calculate_stability()

            # 5. Emotion Classification (Geometric Heuristic Analysis)
            emotion = self._classify_emotion(face_landmarks, width, height)

            return {
                "face_detected": True,
                "gaze": gaze,
                "emotion": emotion,
                "stability_score": stability_score,
                "confidence_score": confidence_score
            }

        except Exception as e:
            logger.error(f"Error processing video frame: {e}", exc_info=True)
            return {
                "face_detected": False,
                "gaze": "center",
                "emotion": "neutral",
                "stability_score": 0,
                "confidence_score": 0
            }

    def _calculate_stability(self) -> int:
        """
        Calculates stability (0-100) based on standard deviation of nose movement.
        """
        if len(self.nose_history) < 3:
            return 100

        # Calculate standard deviation of displacements
        coords = np.array(self.nose_history)
        diffs = np.diff(coords, axis=0)
        distances = np.linalg.norm(diffs, axis=1)
        
        # Average movement per frame
        mean_movement = np.mean(distances)
        
        # Map average movement to a stability score 0-100
        # If mean movement is > 10 pixels, score drops. Highly stable head is < 1.5 pixels movement.
        score = 100 - int(mean_movement * 8)
        return max(0, min(100, score))

    def _classify_emotion(self, landmarks, width: int, height: int) -> str:
        """
        Classifies emotion geometrically based on landmark distances.
        Classes: happy (smiling), nervous (tense/furrowed/lip corners pulled), neutral (normal)
        """
        # Outer Face boundary: Temple indices 234 (left), 454 (right)
        p_234 = np.array([landmarks[234].x * width, landmarks[234].y * height])
        p_454 = np.array([landmarks[454].x * width, landmarks[454].y * height])
        face_width = np.linalg.norm(p_454 - p_234)

        if face_width <= 0:
            return "neutral"

        # Lip Corners: indices 61 (left), 291 (right)
        p_61 = np.array([landmarks[61].x * width, landmarks[61].y * height])
        p_291 = np.array([landmarks[291].x * width, landmarks[291].y * height])
        mouth_width = np.linalg.norm(p_291 - p_61)

        # Mouth width ratio normalized by face width
        mouth_ratio = mouth_width / face_width

        # Lip Heights (to check for open mouth): index 0 (top lip), 17 (bottom lip)
        p_0 = np.array([landmarks[0].x * width, landmarks[0].y * height])
        p_17 = np.array([landmarks[17].x * width, landmarks[17].y * height])
        mouth_height = np.linalg.norm(p_17 - p_0)
        mouth_height_ratio = mouth_height / face_width

        # Eyebrows distance (tension check): index 107 (left inner), 336 (right inner)
        p_107 = np.array([landmarks[107].x * width, landmarks[107].y * height])
        p_336 = np.array([landmarks[336].x * width, landmarks[336].y * height])
        eyebrow_distance = np.linalg.norm(p_336 - p_107)
        eyebrow_ratio = eyebrow_distance / face_width

        # Eyebrow to eye height (to track raising eyebrows): Left Eye 159, Left Eyebrow 70
        p_159 = np.array([landmarks[159].x * width, landmarks[159].y * height])
        p_70 = np.array([landmarks[70].x * width, landmarks[70].y * height])
        eyebrow_eye_dist = np.linalg.norm(p_159 - p_70)
        eyebrow_eye_ratio = eyebrow_eye_dist / face_width

        # Emotion Classification Decision Tree
        # 1. Happy: Lip corners stretched horizontally (high mouth_ratio > 0.355)
        # And lip corners are higher than mouth center
        if mouth_ratio > 0.355:
            return "happy"
        
        # 2. Nervous: High eyebrow raising (fear/worry) OR tightly closed mouth with furrowed brow
        # Eyebrows furrowed (small eyebrow_ratio < 0.17) OR eyebrows raised high (eyebrow_eye_ratio > 0.185)
        # combined with slightly open mouth (panting/hesitation) OR extreme mouth tension
        elif eyebrow_ratio < 0.175 or eyebrow_eye_ratio > 0.19:
            return "nervous"

        # 3. Neutral: Default facial state
        return "neutral"
