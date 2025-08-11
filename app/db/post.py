from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .mixins import UserRelationMixin
from .models import Base


class Post(UserRelationMixin, Base):
    _user_back_populates = "posts"

    title: Mapped[str] = mapped_column(String(100), unique=False)
    body: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}, user_id={self.user_id})"

    def __repr__(self):
        return str(self)

    # USER_ID это пользователь, который создал этот ПОСТ
    # user_id: Mapped[int] = mapped_column(
    #     ForeignKey("users.id"),
    # )

    # user: Mapped["User"] = relationship(back_populates="posts")
