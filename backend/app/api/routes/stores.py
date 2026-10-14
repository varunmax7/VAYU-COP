from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.errors import api_error
from app.models.enums import UserRole
from app.models.stores import StoreInventory
from app.schemas.stores import StoreInventoryRead, StoreInventoryUpdate

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=list[StoreInventoryRead])
def list_stores(
    base: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[StoreInventory]:
    stmt = select(StoreInventory)
    if base:
        stmt = stmt.where(StoreInventory.base_id == base)
    if category:
        stmt = stmt.where(StoreInventory.category == category)
    stmt = stmt.order_by(StoreInventory.id)
    return list(db.scalars(stmt))


@router.patch("/{store_id}", response_model=StoreInventoryRead)
def update_store(
    store_id: str,
    payload: StoreInventoryUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.MAINTENANCE, UserRole.ADMIN)),
) -> StoreInventory:
    store = db.get(StoreInventory, store_id)
    if store is None:
        raise api_error(404, f"Store line {store_id} not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store
