import os
import logging
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Application
    app_name: str = "Pain-to-Idea Generator"
    version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # OpenRouter API
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pain_to_idea.db")

    # Rate Limiting
    rate_limit_runs_per_hour: int = int(os.getenv("RATE_LIMIT_RUNS_PER_HOUR", "5"))

    # Performance
    generation_timeout_seconds: int = int(os.getenv("GENERATION_TIMEOUT_SECONDS", "600"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
