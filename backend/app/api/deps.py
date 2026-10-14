import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import api_error
from app.core.security import decode_access_token
from app.models.enums import UserRole
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise api_error(401, "Invalid or expired token") from exc

    user = db.get(User, payload.get("sub"))
    if user is None:
        raise api_error(401, "User no longer exists")
    return user


def require_roles(*roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise api_error(
                403,
                f"Role {current_user.role} is not permitted to perform this action",
                {"required_roles": [r.value for r in roles]},
            )
        return current_user

    return dependency
