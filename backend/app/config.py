from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "agnidrishti"
    postgres_user: str = "agnidrishti"
    postgres_password: str = "changeme"
    database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    secret_key: str = "changeme"
    firms_api_key: str = ""
    firms_map_key: str = ""
    bhuvan_api_token: str = ""
    # NoDecode: pydantic-settings otherwise tries to json.loads() the raw env
    # string for any list-typed field before this validator runs, which fails
    # on our comma-separated CORS_ORIGINS format (e.g. "a,b") with a
    # SettingsError instead of ever reaching parse_cors_origins below.
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    def model_post_init(self, __context: object) -> None:
        if not self.database_url:
            self.database_url = (
                f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )


settings = Settings()