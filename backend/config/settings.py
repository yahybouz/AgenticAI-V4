"""Application-wide settings and defaults.
Derived from cahier des charges AgenticAI V4.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings


class OllamaModelConfig(BaseModel):
    """Describes a local model exposed by Ollama."""

    name: str
    role: Literal["llm", "embedding", "asr"]
    preset: str | None = None
    max_vram_gb: int | None = None
    quality_profile: Literal["high", "balanced", "fast"] = "balanced"


class MessagingConfig(BaseModel):
    broker: Literal["nats", "redis"] = "redis"
    url: str = "redis://localhost:6379/0"
    stream: str = "agenticai"


class DatabaseConfig(BaseModel):
    postgres_url: str = "postgresql+asyncpg://agenticai:agenticai@localhost:5432/agenticai"
    vector_db: Literal["qdrant", "chroma"] = "qdrant"
    vector_url: str = "http://localhost:6333"
    blob_store: Literal["minio"] = "minio"
    blob_endpoint: str = "http://localhost:9000"
    blob_access_key: str = "agenticai"
    blob_secret_key: str = "agenticai"


class MonitoringThresholds(BaseModel):
    rag_p_at_1_min: float = 0.75
    asr_max_wer: float = 0.18
    asr_max_latency_ms: int = 3000
    email_precision_target: float = 0.87


class SecurityConfig(BaseModel):
    rbac_enabled: bool = True
    audit_trail_enabled: bool = True
    vault_addr: str | None = "http://localhost:8200"
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


class AppSettings(BaseSettings):
    """Centralized configuration for the backend."""

    environment: Literal["local", "staging", "prod"] = "local"
    project_name: str = "AgenticAI V4"
    api_version: str = "4.0.0"
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
        ]
    )
    messaging: MessagingConfig = Field(default_factory=MessagingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    monitoring: MonitoringThresholds = Field(default_factory=MonitoringThresholds)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout_seconds: float = 60.0
    ollama_models: List[OllamaModelConfig] = Field(
        default_factory=lambda: [
            OllamaModelConfig(
                name="llama3:8b-instruct",
                role="llm",
                preset="quality",
                max_vram_gb=10,
            ),
            OllamaModelConfig(
                name="qwen2.5:7b-instruct",
                role="llm",
                preset="balanced",
            ),
            OllamaModelConfig(
                name="mistral:7b-instruct",
                role="llm",
                preset="speed",
            ),
            OllamaModelConfig(
                name="nomic-embed-text",
                role="embedding",
                preset="default",
            ),
            OllamaModelConfig(
                name="whisper:medium",
                role="asr",
                preset="high_accuracy",
            ),
        ]
    )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignorer les variables d'environnement inconnues
    )

    @property
    def SECRET_KEY(self) -> str:
        """Clé secrète pour JWT depuis la config de sécurité"""
        return self.security.secret_key


@lru_cache
def get_settings() -> AppSettings:
    """Return cached settings instance."""

    return AppSettings()


__all__ = ["AppSettings", "get_settings", "OllamaModelConfig"]
