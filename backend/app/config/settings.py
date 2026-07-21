from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "AI Marketing Agent Platform"
    DEBUG: bool = True

    # Google AI
    GEMINI_API_KEY: str

    # Supabase PostgreSQL
    DATABASE_URL: str

    # Upstash Redis
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: str) -> str:
        """
        Supabase URL-কে AsyncPG উপযোগী ড্রাইভারে কনভার্ট করার অটো-ভ্যালিডেটর।
        """
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v


# গ্লোবাল ইনস্ট্যান্স যা পুরো অ্যাপ্লিকেশনে ব্যবহৃত হবে
settings = Settings()

