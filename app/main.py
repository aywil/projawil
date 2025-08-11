import secrets
from contextlib import asynccontextmanager

import jwt
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Depends, HTTPException, status, Form, Body, Request
from datetime import timedelta
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.core.depends import get_current_user
from app.core.rbac import PermissionChecker
from app.core.security import (
    create_jwt_token,
    decode_jwt,
    create_hash_password,
    check_hash_password,
    oauth2_scheme,
    get_user_from_token,
)
from core.config import settings
from api_v1 import router as router_v1
from app.db.models import TokenRefreshRequest, User, UserLogin
from app.db.database import get_user, add_user, r_tokens, USERS_DATA


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Этот маршрут проверяет учетные данные пользователя
# и возвращает JWT токен, если данные правильные.
@app.post("/login/", tags=["Authenticate Users"])
@limiter.limit("5/minute")
async def login(user_in: UserLogin, request: Request):
    # user = get_user(user_in.username)
    # if not user or not check_hash_password(user_in.password, user["password"]):
    for user in USERS_DATA:
        if (
            user["username"] == user_in.username
            and user["password"] == user_in.password
        ):
            token = create_jwt_token(
                {"sub": user_in.username},
                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                "access",
            )
            r_token = create_jwt_token(
                {"sub": user_in.username},
                timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
                "refresh",
            )
            r_tokens[user_in.username] = r_token
            return {
                "access_token": token,
                "refresh_token": r_token,
                "token_type": "bearer",
            }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )


@app.get("/admin/")
@PermissionChecker(["admin"])
async def admin_info(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.username, current_user.roles}! Welcome to the admin page."
    }


@app.get("/user/")
@PermissionChecker(["user"])
async def user_info(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello, {current_user.username, current_user.roles}! Welcome to the user page."
    }


@app.get("/guest/")
@PermissionChecker(["guest", "user"])
async def guest_info(current_user: User = Depends(get_current_user)):
    return {"message" f"Hello, {current_user}. You role is {current_user.roles}"}


@app.get("/about_me/")
async def user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/refresh/", tags=["Authenticate Users"])
async def refresh_token(payload: TokenRefreshRequest, request: Request):
    try:
        decoded = decode_jwt(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        username = decoded.get("sub")
        if not username or r_tokens.get(username) != payload.refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        del r_tokens[username]

        new_access = create_jwt_token(
            {"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access"
        )
        new_refresh = create_jwt_token(
            {"sub": username},
            timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
            "refresh",
        )

        r_tokens[username] = new_refresh

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Этот маршрут защищен и требует токен.
# Если токен действителен, мы возвращаем информацию о пользователе.
@app.get("/protected_resource/", tags=["Authenticate Users"])
async def protected_resource(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Token is not access type",
            )

        username = payload.get("sub")
        user = get_user(username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        if user.roles[0] not in ["user", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Failed role"
            )
        return {"username": username}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/register/", tags=["Registration"])
@limiter.limit("1/minute")
async def register(new_user: User, request: Request):
    user = get_user(new_user.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    add_user(new_user.username, create_hash_password(new_user.password))
    return {"message": "New user created"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
