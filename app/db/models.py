from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)


class User(BaseModel):
    """Модель пользователя с базовыми полями"""

    username: str
    full_name: str | None = None
    email: EmailStr | None = None
    disabled: bool = False
    roles: list[str]  # Список ролей пользователя


class UserLogin(BaseModel):
    """Модель для входа в систему"""

    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True
