import json
import os
import threading
from datetime import datetime
from src.config import LOGS_FILE, LOGS_DIR

class ProctoringEventLogger:
    def __init__(self):
        self._lock = threading.Lock()
        self._ensure_logs_dir()
        
    def _ensure_logs_dir(self):
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        
        if not os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'w') as f:
                json.dump([], f)

    def log_event(self, event_type, severity, details=None):
        """
        Logs an event to the JSON file in a thread-safe manner.
        """
        event = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        with self._lock:
            try:
                logs = self.read_logs()
                logs.append(event)
                with open(LOGS_FILE, 'w') as f:
                    json.dump(logs, f, indent=2)
            except Exception as e:
                print(f"Error logging event: {e}")

    def read_logs(self):
        """
        Reads all logs from the JSON file.
        """
        if not os.path.exists(LOGS_FILE):
            return []
        
        with self._lock:
            try:
                with open(LOGS_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                return []

# Singleton instance
event_logger = ProctoringEventLogger()
