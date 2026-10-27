import os
from pathlib import Path

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _USE_V2_SETTINGS = True
except ImportError:
    from pydantic import BaseModel as BaseSettings
    _USE_V2_SETTINGS = False

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Central configuration loaded from environment variables and .env file.
    All settings can be overridden via environment variables (case-insensitive).
    """
    PROJECT_NAME: str = "Autonomous Personal Task Agent"
    VERSION: str = "2.0.0"
    API_PORT: int = 8000
    UI_PORT: int = 8501

    # ── API Keys ────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USE_MOCK_LLM: bool = os.getenv("USE_MOCK_LLM", "false").lower() in ("true", "1", "yes")

    # ── Filesystem Paths ────────────────────────────────────────────────────
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    DB_PATH: Path = BASE_DIR / "agent_database.db"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "chroma_db"
    EVALUATION_DIR: Path = BASE_DIR / "evaluation"
    DOCS_DIR: Path = BASE_DIR / "docs"

    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str = ""  # Resolved below after class definition

    # ── Execution ───────────────────────────────────────────────────────────
    MAX_RETRIES: int = 3
    DEFAULT_USER_ID: str = "user_default"

    # ── ChromaDB ────────────────────────────────────────────────────────────
    CHROMA_COLLECTION_NAME: str = "user_memories"

    # ── Logging ─────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    if _USE_V2_SETTINGS:
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    else:
        class Config:
            env_file = ".env"
            extra = "ignore"


settings = Settings()

# Resolve DATABASE_URL after instantiation so DB_PATH is available
if not settings.DATABASE_URL:
    object.__setattr__(settings, "DATABASE_URL", f"sqlite:///{settings.DB_PATH}")

# Ensure required directories exist
for _path in [
    settings.DATA_DIR,
    settings.MODELS_DIR,
    settings.CHROMA_PERSIST_DIR,
    settings.EVALUATION_DIR,
    settings.DOCS_DIR,
]:
    _path.mkdir(parents=True, exist_ok=True)
