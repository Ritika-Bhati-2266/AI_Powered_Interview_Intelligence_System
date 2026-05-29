import asyncio
import logging
from typing import Dict, Set, Callable, Awaitable, Any

logger = logging.getLogger(__name__)

# Standard Event Types
class EventType:
    SPEECH_TRANSCRIBED = "speech_transcribed"
    EMOTION_DETECTED = "emotion_detected"
    POSTURE_ANALYZED = "posture_analyzed"
    QUESTION_POSED = "question_posed"
    SESSION_COMPLETED = "session_completed"
    SYSTEM_ALERT = "system_alert"


class Event:
    def __init__(self, event_type: str, session_id: str, data: Any):
        self.event_type = event_type
        self.session_id = session_id
        self.data = data
        self.timestamp = asyncio.get_event_loop().time()

    def __repr__(self):
        return f"<Event type={self.event_type} session={self.session_id}>"


class EventBus:
    def __init__(self):
        # Maps session_id -> (maps event_type -> set of async subscriber callbacks)
        self._subscribers: Dict[str, Dict[str, Set[Callable[[Event], Awaitable[None]]]]] = {}
        # Global subscribers (not bound to specific session)
        self._global_subscribers: Dict[str, Set[Callable[[Event], Awaitable[None]]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(
        self, 
        event_type: str, 
        callback: Callable[[Event], Awaitable[None]], 
        session_id: str = None
    ):
        """Subscribe to a specific event type, optionally filtered by session_id."""
        async with self._lock:
            if session_id:
                if session_id not in self._subscribers:
                    self._subscribers[session_id] = {}
                if event_type not in self._subscribers[session_id]:
                    self._subscribers[session_id][event_type] = set()
                self._subscribers[session_id][event_type].add(callback)
                logger.info(f"Subscribed callback to '{event_type}' for session '{session_id}'")
            else:
                if event_type not in self._global_subscribers:
                    self._global_subscribers[event_type] = set()
                self._global_subscribers[event_type].add(callback)
                logger.info(f"Subscribed global callback to '{event_type}'")

    async def unsubscribe(
        self, 
        event_type: str, 
        callback: Callable[[Event], Awaitable[None]], 
        session_id: str = None
    ):
        """Unsubscribe a callback from an event type."""
        async with self._lock:
            try:
                if session_id:
                    if session_id in self._subscribers and event_type in self._subscribers[session_id]:
                        self._subscribers[session_id][event_type].discard(callback)
                        # Clean up empty sets
                        if not self._subscribers[session_id][event_type]:
                            del self._subscribers[session_id][event_type]
                        if not self._subscribers[session_id]:
                            del self._subscribers[session_id]
                else:
                    if event_type in self._global_subscribers:
                        self._global_subscribers[event_type].discard(callback)
                        if not self._global_subscribers[event_type]:
                            del self._global_subscribers[event_type]
            except Exception as e:
                logger.error(f"Error unsubscribing callback: {e}")

    async def publish(self, event: Event):
        """Publish an event to all matched subscribers asynchronously."""
        tasks = []
        
        # 1. Gather session-specific subscribers
        if event.session_id in self._subscribers:
            session_subs = self._subscribers[event.session_id]
            if event.event_type in session_subs:
                for callback in session_subs[event.event_type]:
                    tasks.append(self._safely_call(callback, event))
                    
        # 2. Gather global subscribers
        if event.event_type in self._global_subscribers:
            for callback in self._global_subscribers[event.event_type]:
                tasks.append(self._safely_call(callback, event))

        if tasks:
            # Execute all handler callbacks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safely_call(self, callback: Callable[[Event], Awaitable[None]], event: Event):
        try:
            await callback(event)
        except Exception as e:
            logger.error(f"Error executing event callback for {event.event_type}: {e}", exc_info=True)


# Global singleton instance of the Event Bus
event_bus = EventBus()
