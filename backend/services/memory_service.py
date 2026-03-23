from __future__ import annotations

import threading
from typing import Dict, List

from config import get_settings
from models.schemas import ChatMessage


settings = get_settings()


class InMemorySessionStore:
    """
    Simple in-memory session store for chat messages.

    NOTE: This is not persistent and is intended for a single-process deployment.
    Use an external store (e.g., Redis, database) for production multi-instance setups.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, List[ChatMessage]] = {}
        self._lock = threading.Lock()

    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append_message(self, session_id: str, message: ChatMessage) -> None:
        with self._lock:
            messages = self._sessions.setdefault(session_id, [])
            messages.append(message)
            self._trim_session_locked(session_id, messages)

    def set_session_messages(self, session_id: str, messages: List[ChatMessage]) -> None:
        with self._lock:
            self._sessions[session_id] = list(messages)
            self._trim_session_locked(session_id, self._sessions[session_id])

    def _trim_session_locked(self, session_id: str, messages: List[ChatMessage]) -> None:
        """
        Trim context when memory grows too large.

        Strategy:
        - Keep at most MAX_SESSION_MESSAGES messages.
        - Additionally, approximate context length by characters and keep the
          most recent messages whose total content length is <= MAX_CONTEXT_CHARS.
        """
        if not messages:
            return

        # First, enforce max number of messages
        if len(messages) > settings.MAX_SESSION_MESSAGES:
            excess = len(messages) - settings.MAX_SESSION_MESSAGES
            del messages[0:excess]

        # Then enforce approximate character-based context budget
        total_chars = 0
        trimmed: List[ChatMessage] = []
        for msg in reversed(messages):
            msg_len = len(msg.content or "")
            if total_chars + msg_len > settings.MAX_CONTEXT_CHARS:
                break
            trimmed.append(msg)
            total_chars += msg_len

        trimmed.reverse()
        self._sessions[session_id] = trimmed


# Global in-memory store instance
session_store = InMemorySessionStore()

