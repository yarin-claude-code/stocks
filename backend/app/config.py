from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    fetch_interval_minutes: int = 5

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")

    class Config:
        env_file = ".env"


settings = Settings()
