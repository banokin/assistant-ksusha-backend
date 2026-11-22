from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GIGACHAT_AUTHORIZATION_KEY: str
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()