from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Load config từ file .env.

    Phase 1 chỉ cần config cơ bản.
    Các phase sau sẽ dùng tiếp để kết nối API, PostgreSQL, ingestion.
    """

    PROJECT_NAME: str = "ecommerce-sales-analytics"
    APP_ENV: str = "local"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "ecommerce_db"
    DB_USER: str = "ecommerce_user"
    DB_PASSWORD: str = "ecommerce_password"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """
        SQLAlchemy/Postgres connection string.
        Sẽ dùng nhiều ở Phase 4, 5, 6.
        """
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()