from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column


class ProvenanceMixin:
    """Per §6.2: stamped on every fused entity so the UI can show source/age/confidence."""

    source: Mapped[str] = mapped_column(String(64), default="seed")
    source_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fused_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    stale: Mapped[bool] = mapped_column(Boolean, default=False)
