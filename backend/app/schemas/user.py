from app.models.enums import UserRole
from app.schemas.common import CamelModel


class UserRead(CamelModel):
    id: str
    username: str
    display_name: str
    role: UserRole
