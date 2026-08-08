from typing import Dict, Any

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create(self, session_id: str, candidate_data: Dict[str, Any] = None) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "candidate": candidate_data or {},
                "history": [],
                "turn_count": 0,
                "is_completed": False
            }
        elif candidate_data and not self.sessions[session_id]["candidate"]:
            self.sessions[session_id]["candidate"] = candidate_data

        return self.sessions[session_id]

session_manager = SessionManager()