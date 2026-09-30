from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fraud Rule Engine"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AWS Placeholders
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SNS_TOPIC_ARN: Optional[str] = None
    AWS_SES_SENDER_EMAIL: Optional[str] = None

    # TigerGraph Settings
    TIGERGRAPH_HOST: str = "http://localhost"
    TIGERGRAPH_GRAPH: str = "FraudGraph"
    TIGERGRAPH_SECRET: Optional[str] = None
    TIGERGRAPH_TOKEN: Optional[str] = None
    TIGERGRAPH_USERNAME: Optional[str] = "tigergraph"
    TIGERGRAPH_PASSWORD: Optional[str] = "tigergraph"
    TIGERGRAPH_RESTPP_PORT: int = 9000
    TIGERGRAPH_GS_PORT: int = 14240

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
