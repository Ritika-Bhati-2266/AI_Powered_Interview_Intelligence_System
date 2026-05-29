import uuid
from typing import Dict, List, Any, Optional, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class InterviewSession:
    def __init__(self, session_id: str, candidate_name: str, resume_data: Optional[Dict[str, Any]] = None):
        self.session_id = session_id
        self.candidate_name = candidate_name
        self.resume_data = resume_data or {}
        self.questions: List[Dict[str, Any]] = []
        self.current_question_index: int = -1
        self.active_connections: Set[WebSocket] = set()
        
        # Performance and analysis metrics aggregated during the interview
        self.metrics: Dict[str, Any] = {
            "speech_transcripts": [],     # List of transcripts with timestamps
            "emotion_scores": [],         # Emotion timeline from CV engine
            "posture_logs": [],           # Posture timeline from CV engine
            "filler_words_count": 0,
            "overall_feedback": None
        }

    async def broadcast_json(self, data: Dict[str, Any]):
        """Send JSON data to all active websockets in this session."""
        if not self.active_connections:
            return
        
        closed_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send message to websocket in session {self.session_id}: {e}")
                closed_connections.add(connection)
                
        # Clean up failed connections
        if closed_connections:
            self.active_connections -= closed_connections


class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, InterviewSession] = {}

    def create_session(self, candidate_name: str, resume_data: Optional[Dict[str, Any]] = None) -> InterviewSession:
        """Create a new interview session with a unique ID."""
        session_id = str(uuid.uuid4())
        session = InterviewSession(session_id=session_id, candidate_name=candidate_name, resume_data=resume_data)
        self.active_sessions[session_id] = session
        logger.info(f"Created session {session_id} for candidate {candidate_name}")
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Retrieve an active session by its ID."""
        return self.active_sessions.get(session_id)

    async def register_connection(self, session_id: str, websocket: WebSocket) -> bool:
        """Register a new WebSocket connection to a session."""
        session = self.get_session(session_id)
        if session:
            session.active_connections.add(websocket)
            logger.info(f"Registered connection for session {session_id}. Active connections: {len(session.active_connections)}")
            return True
        logger.warning(f"Attempted to register connection to non-existent session {session_id}")
        return False

    async def remove_connection(self, session_id: str, websocket: WebSocket):
        """Remove a WebSocket connection from a session."""
        session = self.get_session(session_id)
        if session:
            session.active_connections.discard(websocket)
            logger.info(f"Removed connection for session {session_id}. Remaining active connections: {len(session.active_connections)}")
            # Cleanup session if no connections are left and no resume data is kept (optional)
            # Here we keep session state in memory for REST querying later

    def delete_session(self, session_id: str):
        """Remove a session from memory."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Deleted session {session_id} from SessionManager")


# Global singleton instance of SessionManager
session_manager = SessionManager()
