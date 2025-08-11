import secrets
from app.db.models import User

USERS_DATA = [
    {
        "username": "admin",
        "password": "adminpass",  # В продакшене пароли должны быть хешированы!
        "roles": ["admin"],
        "full_name": "Admin User",
        "email": "admin@example.com",
        "disabled": False,
    },
    {
        "username": "user",
        "password": "userpass",
        "roles": ["user"],
        "full_name": "Regular User",
        "email": "user@example.com",
        "disabled": False,
    },
    {
        "username": "guest",
        "password": "guestpass",
        "roles": ["guest"],
        "full_name": "Regular User",
        "email": "user@example.com",
        "disabled": False,
    },
]
r_tokens = {}


def add_user(username, password):
    USERS_DATA.append({"username": username, "password": password})


def get_user(username: str):
    # Функция для поиска пользователя по имени пользователя.
    # В реальном проекте это должно быть запросом к базе данных.
    for user in USERS_DATA:
        if secrets.compare_digest(user.get("username"), username):
            return User(**{k: v for k, v in user.items() if k != "password"})
    return None
