import json
import logging
import os
import sys
import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from app.core.config import settings
from app.core.event_bus import event_bus, Event, EventType
from app.services.session_manager import session_manager, InterviewSession

# Dynamic import of CV Engine Processor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
try:
    from cv_engine.src.processor import CVFrameProcessor
    CV_AVAILABLE = True
except Exception as e:
    logging.getLogger("backend-main").warning(f"Could not import CVFrameProcessor: {e}")
    CV_AVAILABLE = False


# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("backend-main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Starting up AI Interview Intelligence System Backend...")
    yield
    # Shutdown tasks
    logger.info("Shutting down AI Interview Intelligence System Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST HTTP Health Endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verify backend system status and service health."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "active_sessions_count": len(session_manager.active_sessions),
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "vosk_model_path": settings.VOSK_MODEL_PATH
    }

# WebSocket Endpoint for Real-time Interview Session Ingestion & Signaling
@app.websocket("/ws/interview")
async def websocket_interview(
    websocket: WebSocket,
    session_id: str = Query(..., description="The unique session ID for the candidate's interview")
):
    """
    WebSocket endpoint for bidirectional real-time audio streaming, computer vision telemetry, 
    and question presentation signaling.
    """
    # 1. Retrieve the session state
    session: InterviewSession = session_manager.get_session(session_id)
    if not session:
        logger.error(f"WebSocket connection rejected: Session {session_id} not found.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not found")
        return

    # 2. Accept the WebSocket connection
    await websocket.accept()
    await session_manager.register_connection(session_id, websocket)
    logger.info(f"WebSocket connected for session {session_id} (Candidate: {session.candidate_name})")

    # 3. Define event bus listener for this specific session
    # Whenever an event for this session is published, broadcast it to the candidate's websocket
    async def session_event_listener(event: Event):
        try:
            await websocket.send_json({
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "data": event.data
            })
        except Exception as e:
            logger.error(f"Error sending event to WebSocket in session {session_id}: {e}")

    # Register our listener on the event bus
    await event_bus.subscribe(EventType.SPEECH_TRANSCRIBED, session_event_listener, session_id)
    await event_bus.subscribe(EventType.EMOTION_DETECTED, session_event_listener, session_id)
    await event_bus.subscribe(EventType.POSTURE_ANALYZED, session_event_listener, session_id)
    await event_bus.subscribe(EventType.QUESTION_POSED, session_event_listener, session_id)
    await event_bus.subscribe(EventType.SYSTEM_ALERT, session_event_listener, session_id)

    # Send initial success greeting
    await websocket.send_json({
        "event_type": "connection_established",
        "data": {
            "session_id": session_id,
            "candidate_name": session.candidate_name,
            "status": "ready"
        }
    })

    try:
        # 4. Bidirectional Ingestion Loop
        while True:
            # We receive text (JSON commands) or raw audio bytes (PCM/WebM)
            message = await websocket.receive()
            
            # Case A: Binary raw audio chunk received (Real-time Speech-to-Text streaming)
            if "bytes" in message:
                audio_bytes: bytes = message["bytes"]
                # In Step 4/speech-engine we will pipe this directly into Vosk / speech module.
                # For now, we simulate receipt and log details.
                # In production, we yield these bytes to speech-engine and publish results to the EventBus.
                pass

            # Case B: Text (JSON commands) received
            elif "text" in message:
                try:
                    payload = json.loads(message["text"])
                    command = payload.get("command")
                    data = payload.get("data", {})
                    
                    logger.info(f"Received WebSocket command '{command}' in session {session_id}")

                    if command == "ping":
                        await websocket.send_json({"event_type": "pong", "data": {}})
                        
                    elif command == "start_interview":
                        # Post a system alert event on the event bus
                        event = Event(
                            event_type=EventType.SYSTEM_ALERT,
                            session_id=session_id,
                            data={"message": "Interview session started. Live streaming active."}
                        )
                        await event_bus.publish(event)
                        
                    elif command == "telemetry_cv":
                        # Client submits real-time emotion/posture calculations
                        emotion = data.get("emotion")
                        posture = data.get("posture")
                        
                        if emotion:
                            session.metrics["emotion_scores"].append(emotion)
                            # Publish event to any backend analytics dashboards or logger
                            await event_bus.publish(Event(
                                event_type=EventType.EMOTION_DETECTED,
                                session_id=session_id,
                                data={"emotion": emotion}
                            ))
                        if posture:
                            session.metrics["posture_logs"].append(posture)
                            await event_bus.publish(Event(
                                event_type=EventType.POSTURE_ANALYZED,
                                session_id=session_id,
                                data={"posture": posture}
                            ))
                            
                    else:
                        logger.warning(f"Unknown command received on WebSocket: {command}")
                        await websocket.send_json({
                            "event_type": "error",
                            "data": {"message": f"Unknown command: {command}"}
                        })
                except json.JSONDecodeError:
                    logger.error("Failed to decode text message as JSON on WebSocket.")
                    await websocket.send_json({
                        "event_type": "error",
                        "data": {"message": "Invalid JSON format"}
                    })
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected gracefully for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {e}", exc_info=True)
    finally:
        # 5. Clean up WebSocket connection & Event Bus subscriptions
        await session_manager.remove_connection(session_id, websocket)
        await event_bus.unsubscribe(EventType.SPEECH_TRANSCRIBED, session_event_listener, session_id)
        await event_bus.unsubscribe(EventType.EMOTION_DETECTED, session_event_listener, session_id)
        await event_bus.unsubscribe(EventType.POSTURE_ANALYZED, session_event_listener, session_id)
        await event_bus.unsubscribe(EventType.QUESTION_POSED, session_event_listener, session_id)
        await event_bus.unsubscribe(EventType.SYSTEM_ALERT, session_event_listener, session_id)
        logger.info(f"WebSocket cleanup complete for session {session_id}")
