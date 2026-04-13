from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseModel):
    app_name: str = Field(default="CPT208 RAG Service", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    ragflow_api_key: str = Field(alias="RAGFLOW_API_KEY")
    ragflow_base_url: str = Field(default="http://127.0.0.1:9380", alias="RAGFLOW_BASE_URL")
    ragflow_health_page_size: int = Field(default=1, alias="RAGFLOW_HEALTH_PAGE_SIZE")
    default_dataset_name: str = Field(default="default", alias="DEFAULT_DATASET_NAME")
    metadata_db_path: str = Field(default=str(ROOT_DIR / "data" / "kb_metadata.db"), alias="METADATA_DB_PATH")
    upload_max_file_size_mb: int = Field(default=20, alias="UPLOAD_MAX_FILE_SIZE_MB")
    llm_provider: str = Field(default="ragflow_chat", alias="LLM_PROVIDER")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_model: str = Field(default="deepseek-ai/DeepSeek-V3@SILICONFLOW", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    llm_top_p: float = Field(default=0.3, alias="LLM_TOP_P")
    llm_max_tokens: int = Field(default=512, alias="LLM_MAX_TOKENS")
    rag_context_max_chars: int = Field(default=12000, alias="RAG_CONTEXT_MAX_CHARS")
    ragflow_retry_attempts: int = Field(default=3, alias="RAGFLOW_RETRY_ATTEMPTS")
    ragflow_retry_delay_seconds: float = Field(default=1.0, alias="RAGFLOW_RETRY_DELAY_SECONDS")
    llm_timeout_seconds: int = Field(default=60, alias="LLM_TIMEOUT_SECONDS")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_env(cls) -> "Settings":
        import os

        try:
            return cls.model_validate(os.environ)
        except ValidationError as exc:
            raise RuntimeError(f"Invalid application configuration: {exc}") from exc


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
