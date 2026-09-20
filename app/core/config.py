from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Majburiy — .env faylida bo'lmasa, ilova ishga tushmaydi
    DATABASE_URL: str = Field(...)
    BOT_TOKEN: str = Field(...)
    ANTHROPIC_API_KEY: str = Field(...)
    GROQ_API_KEY: str = Field(...)
    SECRET_KEY: str = Field(..., min_length=32)

    # Ixtiyoriy, xavfsiz standart qiymatlar bilan
    REDIS_URL: str = "redis://localhost:6379"
    ENVIRONMENT: str = "development"

    # Qo'shimcha AI providerlar — ixtiyoriy (bo'sh bo'lsa, ai_service
    # shu providerni fallback zanjiridan avtomatik chetlab o'tadi,
    # ilova ishga tushishiga xalaqit bermaydi)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Ruxsat etilgan frontend domenlari (vergul bilan ajratilgan)
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
