from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://jogai:password@postgres:5432/jogai"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Telegram
    telegram_bot_token: str = ""
    telegram_channel_br_id: str = ""
    telegram_channel_mx_id: str = ""

    # AI
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-20250514"

    # Affiliate
    pinup_ref_id: str = ""
    onewin_ref_id: str = ""
    starda_ref_id: str = ""

    # Auth
    secret_key: str = "change-me-in-production"

    # App
    app_url: str = "https://jogai.fun"
    environment: str = "development"

    # i18n
    default_locale: str = "pt_BR"
    default_geo: str = "BR"

    # External APIs
    odds_api_key: str = ""
    football_api_key: str = ""

    # Analytics
    posthog_key: str = ""


settings = Settings()
