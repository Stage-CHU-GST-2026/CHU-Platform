"""Manages agent sessions (thread_id -> agent instance)."""

from __future__ import annotations

import time
import uuid

from langgraph.checkpoint.base import BaseCheckpointSaver

from .agent_service import AgentService


class SessionManager:
    """Manages agent sessions with a pluggable checkpointer backend.

    Uses an in-memory session registry but delegates conversation
    persistence to the injected checkpointer (InMemory ↔ Postgres).
    """

    _TTL_SECONDS = 3600  # 1 hour

    def __init__(self) -> None:
        self._sessions: dict[str, _SessionEntry] = {}
        self._checkpointer: BaseCheckpointSaver | None = None

    def set_checkpointer(self, checkpointer: BaseCheckpointSaver) -> None:
        """Inject a checkpointer (e.g. Postgres) after construction.

        Called during the app lifespan so the checkpointer is ready
        before any request arrives.
        """
        self._checkpointer = checkpointer

    def get_or_create(self, thread_id: str | None = None) -> str:
        """Return an existing thread_id or create a new one."""
        tid = thread_id or str(uuid.uuid4())
        if tid not in self._sessions:
            self._sessions[tid] = _SessionEntry(
                AgentService(checkpointer=self._checkpointer)
            )
        self._sessions[tid].touch()
        self._evict_expired()
        return tid

    def get_agent(self, thread_id: str) -> AgentService | None:
        entry = self._sessions.get(thread_id)
        if entry is None:
            return None
        entry.touch()
        return entry.service

    def remove(self, thread_id: str) -> None:
        self._sessions.pop(thread_id, None)

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [
            tid for tid, entry in self._sessions.items()
            if now - entry.created > self._TTL_SECONDS
        ]
        for tid in expired:
            del self._sessions[tid]


# ── Shared singleton ────────────────────────────────────────────
# Both chat.py and conversations.py import this so the Postgres
# checkpointer injected via main.py is shared by all endpoints.
session_manager = SessionManager()


class _SessionEntry:
    __slots__ = ("service", "created")

    def __init__(self, service: AgentService) -> None:
        self.service = service
        self.created = time.monotonic()

    def touch(self) -> None:
        self.created = time.monotonic()
