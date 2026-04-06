from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC_TRANSACTIONS: str = "transactions"
    KAFKA_GROUP_ID: str = "antifraud-service"
    
    PROJECT_NAME: str = "Antifraud Service"
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
