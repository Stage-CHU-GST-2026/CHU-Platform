"""Artifact ORM model — generated plots linked to conversations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

if TYPE_CHECKING:
    from api.models.conversation import Conversation


class Artifact(Base):
    """A generated file (plot / chart) attached to a conversation."""

    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Original filename on disk.",
    )
    filepath: Mapped[str] = mapped_column(
        String(512), nullable=False,
        comment="Absolute path to the file on disk.",
    )
    mime_type: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="MIME type (e.g. image/png).",
    )
    file_size: Mapped[int | None] = mapped_column(
        nullable=True,
        comment="File size in bytes.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ── Relationships ──
    conversation: Mapped[Conversation] = relationship(
        back_populates="artifacts",
    )

    def __repr__(self) -> str:
        return f"<Artifact {self.id!r} file={self.filename!r}>"
