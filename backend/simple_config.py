"""
Simple configuration for Smart Financial Advisor
"""
import os

class Settings:
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_RELOAD = True
    DEBUG = True
    LOG_LEVEL = "INFO"
    
    # CORS
    CORS_ORIGINS = ["*"]
    
    # External APIs (optional)
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    
    # Model Settings
    SEQUENCE_LENGTH = 60
    PREDICTION_DAYS = 30
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001
    EPOCHS = 100
    PATIENCE = 15
    
    # Technical Indicators
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STD = 2
    
    # Data Settings
    TRAINING_YEARS = 2
    MIN_DATA_POINTS = 200
    TEST_SIZE = 0.2
    
    # Risk Settings
    RISK_FREE_RATE = 0.02
    VAR_CONFIDENCE_95 = 1.65
    VAR_CONFIDENCE_99 = 2.33

settings = Settings()
