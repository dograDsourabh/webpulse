from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pagespeed_api_key: str = Field(default="", alias="PAGESPEED_API_KEY")
    frontend_url: str = Field(
        default="http://localhost:5173",
        alias="FRONTEND_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
