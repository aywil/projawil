from fastapi import Depends, HTTPException, status
from app.core.security import get_user_from_token
from app.db.database import get_user
from app.db.models import User


def get_current_user(current_username: str = Depends(get_user_from_token)) -> User:
    user = get_user(current_username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
