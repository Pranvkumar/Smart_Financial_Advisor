"""
Configuration settings for Smart Financial Advisor
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    
    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "financial_advisor")
    
    # Redis Cache
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    CACHE_EXPIRY: int = 3600  # 1 hour
    
    # Model Settings
    MODEL_RETRAIN_DAYS: int = int(os.getenv("MODEL_RETRAIN_DAYS", 7))
    PREDICTION_DAYS: int = int(os.getenv("PREDICTION_DAYS", 30))
    SEQUENCE_LENGTH: int = 60  # Days of historical data for LSTM
    
    # Stock Data
    DEFAULT_START_DATE: str = "2020-01-01"
    DATA_UPDATE_INTERVAL: int = 300  # seconds (5 minutes)
    
    # Technical Indicators
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BB_PERIOD: int = 20
    BB_STD: int = 2
    
    # Sentiment Analysis
    SENTIMENT_BATCH_SIZE: int = 32
    NEWS_LOOKBACK_DAYS: int = 7
    SENTIMENT_THRESHOLD: float = 0.3
    
    # Portfolio Optimization
    MIN_STOCKS: int = 3
    MAX_STOCKS: int = 20
    RISK_FREE_RATE: float = 0.04  # 4% annual
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    CORS_ORIGINS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/financial_advisor.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
