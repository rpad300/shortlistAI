"""
Configuration module for CV Analysis Platform.

Loads and validates all environment variables and provides
centralized access to configuration throughout the application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive configuration (API keys, database credentials) must be
    provided through environment variables, never hardcoded.
    """
    
    # Application
    app_env: str = Field(default="development", env="APP_ENV")
    app_port: int = Field(default=8000, env="APP_PORT")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    secret_key: str = Field(default="dev-secret-key-CHANGE-IN-PRODUCTION", env="SECRET_KEY")
    
    # Database (Supabase)
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # AI Providers
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    kimi_api_key: Optional[str] = Field(default=None, env="KIMI_API_KEY")
    minimax_api_key: Optional[str] = Field(default=None, env="MINIMAX_API_KEY")
    minimax_group_id: Optional[str] = Field(default=None, env="MINIMAX_GROUP_ID")
    
    # Email Service
    resend_api_key: Optional[str] = Field(default=None, env="RESEND_API_KEY")
    from_email: str = Field(default="noreply@shortlistai.com", env="FROM_EMAIL")
    
    # Security
    admin_password_hash: str = Field(
        default="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILY8T6eBO",
        env="ADMIN_PASSWORD_HASH"
    )
    
    # Rate Limiting & Abuse Prevention
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")
    max_cv_file_size_mb: int = Field(default=10, env="MAX_CV_FILE_SIZE_MB")
    max_job_posting_length: int = Field(default=50000, env="MAX_JOB_POSTING_LENGTH")
    
    # Feature Flags
    enable_ai_translation: bool = Field(default=True, env="ENABLE_AI_TRANSLATION")
    enable_candidate_flow: bool = Field(default=True, env="ENABLE_CANDIDATE_FLOW")
    enable_interviewer_flow: bool = Field(default=True, env="ENABLE_INTERVIEWER_FLOW")
    
    @validator("app_env")
    def validate_env(cls, v):
        """Ensure app_env is one of the allowed values."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = "../../.env"  # .env is in project root
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
# Import this throughout the application to access configuration
settings = Settings()

