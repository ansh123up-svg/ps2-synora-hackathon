from collections import defaultdict
from typing import List, Dict, Any, Optional
import time

# session_id -> {messages, health_conditions, metadata}
_sessions: Dict[str, Dict] = defaultdict(lambda: {
    "messages": [],
    "health_conditions": [],
    "last_mode": "wellness",
    "created": time.time(),
    "msg_count": 0,
})

def get_session(sid: str) -> Dict:
    return _sessions[sid]

def get_history(sid: str) -> List[Dict]:
    return _sessions[sid]["messages"]

def append_message(sid: str, role: str, content: str):
    _sessions[sid]["messages"].append({"role": role, "content": content})
    _sessions[sid]["msg_count"] += 1

def set_conditions(sid: str, conditions: List[str]):
    _sessions[sid]["health_conditions"] = conditions

def get_conditions(sid: str) -> List[str]:
    return _sessions[sid].get("health_conditions", [])

def reset_session(sid: str):
    _sessions[sid] = {
        "messages": [],
        "health_conditions": [],
        "last_mode": "wellness",
        "created": time.time(),
        "msg_count": 0,
    }

def set_mode(sid: str, mode: str):
    _sessions[sid]["last_mode"] = mode

def get_mode(sid: str) -> str:
    return _sessions[sid].get("last_mode", "wellness")
