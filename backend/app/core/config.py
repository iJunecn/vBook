"""应用配置：通过 .env 加载"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- 应用基础 ----
    APP_NAME: str = "贝壳易书"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ---- 安全 ----
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # ---- 数据库 ----
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR / 'data' / 'vbook.db'}"

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # ---- 文件存储 ----
    UPLOAD_DIR: str = str(BACKEND_DIR / "uploads")
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp,image/jpg"

    # ---- 微信小程序登录 ----
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""

    # ---- agnes 大模型（OpenAI 兼容接口）----
    AGNES_API_KEY: str = ""
    AGNES_BASE_URL: str = "https://agnes-ai.com"
    AGNES_MODEL: str = "agnes-2.0-flash"
    AGNES_TIMEOUT: int = 60

    # ---- PaddleOCR ----
    PADDLE_OCR_URL: str = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
    PADDLE_OCR_TOKEN: str = ""
    PADDLE_OCR_MODEL: str = "PP-OCRv6"
    PADDLE_OCR_TIMEOUT: int = 60
    PADDLE_OCR_POLL_INTERVAL: float = 1.5
    PADDLE_OCR_MAX_POLLS: int = 40

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_image_type_list(self) -> list[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    Path(s.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    if s.DATABASE_URL.startswith("sqlite:///"):
        db_path = Path(s.DATABASE_URL.replace("sqlite:///", "", 1))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return s


settings = get_settings()
