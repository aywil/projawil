from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .mixins import UserRelationMixin
from .models import Base


class Profile(UserRelationMixin, Base):
    _user_id_unique = True
    _user_back_populates = "profile"

    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None]


class User(Base):
    clipped: Mapped[str | None] = mapped_column(String(20))

    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
