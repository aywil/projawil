import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLE_PERMISSIONS = {
    "admin": ["create", "read", "update", "delete"],
    "user": ["read", "update"],
    "guest": ["read"],
}


def check_permission(user_roles: list[str], required_perm: str):
    for role in user_roles:
        if required_perm in ROLE_PERMISSIONS.get(role, []):
            return True
    return False


# Функция для создания JWT токена.
# Мы копируем входные данные, добавляем время истечения и кодируем токен.
def create_jwt_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    to_encode["type"] = token_type
    expire = datetime.now() + expires_delta

    to_encode.update({"exp": int(expire.timestamp())})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Получаем имя пользователя по JWT-Токен
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt(token=token)
        return payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен устарел",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации",
        )


# Функция для извлечения информации о пользователе из токена.
# Проверяем токен и извлекаем утверждение о пользователе.
def decode_jwt(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)


def create_hash_password(password: str):
    return pwd_context.hash(password)


def check_hash_password(plain_pass: str, hash_pass: str):
    return pwd_context.verify(plain_pass, hash_pass)
