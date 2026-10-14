import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.core.db import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.services.ws_manager import manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    user_id = None
    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
        except jwt.PyJWTError:
            user_id = None

    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        user_exists = db.get(User, user_id) is not None
    finally:
        db.close()
    if not user_exists:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # clients don't send anything; just detect disconnect
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
