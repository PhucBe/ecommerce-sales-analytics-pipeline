from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ecommerce Mock API"
    app_env: str = "dev"
    faker_seed: int = 42
    customer_count: int = 1000
    product_count: int = 500
    order_count: int = 5000
    default_limit: int = 100
    max_limit: int = 500
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()