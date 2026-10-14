from app.schemas.common import CamelModel
from app.schemas.user import UserRead


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
