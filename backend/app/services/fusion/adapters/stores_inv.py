import random
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stores import StoreInventory
from app.services.fusion.adapters.base import SourceAdapter
from app.services.fusion.normaliser import STORE_CODE_MAP

_REVERSE_CODE_MAP = {v: k for k, v in STORE_CODE_MAP.items()}


class StoresInvAdapter(SourceAdapter):
    """Stores Inventory: per-base counts keyed by legacy store codes (e.g. "S-AD1")."""

    name = "stores_inv"
    interval_s = 60.0

    def generate(self, db: Session, rng: random.Random, now: datetime) -> list[dict]:
        lines = list(db.scalars(select(StoreInventory)))
        if not lines:
            return []

        sample = rng.sample(lines, k=min(3, len(lines)))
        return [
            {
                "base": line.base_id,
                "code": _REVERSE_CODE_MAP.get(line.category, line.category),
                "qty_avail": line.available,
                "qty_resv": line.reserved,
                "ts_utc": datetime.now(UTC).isoformat(),
            }
            for line in sample
        ]
