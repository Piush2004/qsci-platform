from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "QSCI API"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
settings = Settings()
