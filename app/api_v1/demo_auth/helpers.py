from datetime import timedelta

from app.auth import utils as auth_utils
from app.core.config import settings
from app.db.models import UserSchema

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)

    return auth_utils.encode_jwt(payload=jwt_payload)


def create_access_token(user: UserSchema):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }

    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
    )


def create_refresh_token(user: UserSchema):
    jwt_payload = {
        "sub": user.username,
        # "username": user.username,
    }

    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
    )
