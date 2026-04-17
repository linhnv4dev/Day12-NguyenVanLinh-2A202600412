from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "Language Tutor Agent"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Server config
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Security
    agent_api_key: str = os.getenv("AGENT_API_KEY", "default-dev-key")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Limits
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    monthly_budget_usd: float = float(os.getenv("MONTHLY_BUDGET_USD", "10.0"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # OpenAI Model
    llm_model: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    class Config:
        env_file = ".env"

settings = Settings()
