from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GIGACHAT_AUTHORIZATION_KEY: str
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()