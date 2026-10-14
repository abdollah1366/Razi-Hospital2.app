from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_JWT_SECRET = "dev-only-change-me-dev-only-change-me"
# کلید Fernet فقط برای توسعه؛ در محیط عملیاتی باید از متغیر محیطی خوانده شود.
_DEV_DATA_KEY = "ZGV2LW9ubHktZGF0YS1rZXktMzItYnl0ZXMtbG9uZyE="


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAZI_", env_file=".env", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+psycopg://razi:razi@localhost:5432/razi"
    jwt_secret: str = _DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    data_encryption_key: str = _DEV_DATA_KEY
    cors_origins: list[str] = []
    max_failed_logins: int = 5
    lockout_minutes: int = 15
    bootstrap_admin_code: str | None = None
    bootstrap_admin_password: str | None = None

    def check_production(self) -> None:
        if self.env != "production":
            return
        if self.jwt_secret == _DEV_JWT_SECRET or len(self.jwt_secret) < 32:
            raise RuntimeError("RAZI_JWT_SECRET باید در محیط عملیاتی تنظیم شود (حداقل ۳۲ نویسه)")
        if self.data_encryption_key == _DEV_DATA_KEY:
            raise RuntimeError("RAZI_DATA_ENCRYPTION_KEY باید در محیط عملیاتی تنظیم شود")


@lru_cache
def get_settings() -> Settings:
    return Settings()
