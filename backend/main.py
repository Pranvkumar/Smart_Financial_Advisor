"""
Main FastAPI application for Smart Financial Advisor
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import routes and settings
from simple_config import settings
from routes import prediction, sentiment, portfolio

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Financial Advisor API",
    description="AI-powered stock prediction and portfolio optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Include routers
app.include_router(prediction.router)
app.include_router(sentiment.router)
app.include_router(portfolio.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Smart Financial Advisor API...")
    logger.info(f"API running on http://{settings.API_HOST}:{settings.API_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Smart Financial Advisor API...")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    try:
        html_file = frontend_path / "index.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text(), status_code=200)
        return {"message": "Smart Financial Advisor API", "version": "1.0.0"}
    except Exception:
        return {"message": "Smart Financial Advisor API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "online",
            "cache": "online",
            "model": "loaded"
        }
    }


@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {
        "name": "Smart Financial Advisor",
        "version": "1.0.0",
        "features": [
            "Stock Price Prediction (LSTM)",
            "Sentiment Analysis",
            "Portfolio Optimization",
            "Risk Assessment",
            "Strategy Backtesting"
        ],
        "endpoints": {
            "prediction": "/api/predict/{symbol}",
            "sentiment": "/api/sentiment/{symbol}",
            "portfolio": "/api/portfolio/*",
            "backtest": "/api/backtest/*"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
