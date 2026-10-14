from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.enums import AlertSeverity


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    severity: Mapped[AlertSeverity] = mapped_column(String(16))
    category: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(String(256))
    entity_refs: Mapped[list] = mapped_column(JSON, default=list)  # [{"kind","id"}, ...]
    dedup_key: Mapped[str] = mapped_column(String(128), index=True)
    acknowledged_by: Mapped[str | None] = mapped_column(String(32), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
