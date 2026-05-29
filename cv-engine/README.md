# Computer Vision Assessment Engine

This engine processes high-fidelity video feeds locally to assess candidate engagement, eye contact, and ergonomic posture.

## Features
- **Emotion Tracking**: Identifies shifts in candidate confidence, focus, and anxiety using facial landmark structures.
- **Gaze Monitoring**: Evaluates camera/eye alignment to determine eye-contact frequency.
- **Posture Calibration**: Recognizes excessive leaning, slump, or shifting using body landmark orientation.

## Usage
Dependencies:
```bash
pip install -r requirements.txt
```
Run `CVFrameProcessor().process_frame(bytes)` to evaluate custom frame buffers.
