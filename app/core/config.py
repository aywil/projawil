import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

load_dotenv()


class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = True


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    # access_token_exp_minutes: int = 3
    access_token_exp_minutes: int = 15


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"

    db: DbSettings = DbSettings()

    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()


SECRET_KEY = os.getenv("SECRET_KEY", "your_dev_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_MINUTES = 3
