from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb+srv://varshitha24bcs10271_db_user:DDYkMTYCcak792NC@cluster0.hv6hf3n.mongodb.net/?appName=Cluster0"
    DATABASE_NAME: str = "burnout_beacon"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"]
    JWT_SECRET: str = "change-me-in-production-use-a-real-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
