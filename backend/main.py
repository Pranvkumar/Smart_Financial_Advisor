"""
Main FastAPI application for Smart Financial Advisor
Enhanced with modern patterns, caching, and improved error handling
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import routes and settings
from simple_config import settings
from routes import prediction, sentiment, portfolio, auth

# Configure logging with better format
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)


# Simple in-memory cache for API responses
class SimpleCache:
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache = {}
        self._timestamps = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str):
        if key in self._cache:
            if datetime.now() - self._timestamps[key] < timedelta(seconds=self.default_ttl):
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value, ttl: int = None):
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def clear(self):
        self._cache.clear()
        self._timestamps.clear()
    
    @property
    def stats(self):
        return {"items": len(self._cache), "keys": list(self._cache.keys())[:10]}

# Global cache instance
cache = SimpleCache()


def is_cuda_available():
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False


# Lifespan context manager (modern replacement for deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Smart Financial Advisor API...")
    logger.info(f"📍 API running on http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"📊 Device: {'CUDA' if is_cuda_available() else 'CPU'}")
    yield
    # Shutdown
    logger.info("👋 Shutting down Smart Financial Advisor API...")
    cache.clear()


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Smart Financial Advisor API",
    description="""
    🤖 **AI-powered stock prediction and portfolio optimization**
    
    ## Features
    - **Stock Prediction**: LSTM neural network for price forecasting
    - **Sentiment Analysis**: News-based market sentiment scoring
    - **Portfolio Optimization**: Modern Portfolio Theory with Sharpe ratio optimization
    - **Risk Assessment**: VaR, volatility, and diversification metrics
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    if process_time > 2.0:
        logger.warning(f"⚠️ Slow request: {request.url.path} took {process_time:.2f}s")
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


# Mount static files - serve from project root directory
root_path = Path(__file__).parent.parent
frontend_path = root_path

# Include routers
app.include_router(prediction.router)
app.include_router(sentiment.router)
app.include_router(portfolio.router)
app.include_router(auth.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    try:
        html_file = frontend_path / "index.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text(encoding='utf-8'), status_code=200)
        return HTMLResponse(content="<h1>Smart Financial Advisor API</h1><p>Visit <a href='/docs'>/docs</a></p>", status_code=200)
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return HTMLResponse(content="<h1>Smart Financial Advisor API</h1>", status_code=200)


@app.get("/login.html", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    """Serve the login page"""
    try:
        html_file = frontend_path / "login.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text(encoding='utf-8'), status_code=200)
        return HTMLResponse(content="<h1>Login page not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving login.html: {e}")
        return HTMLResponse(content="<h1>Error loading login page</h1>", status_code=500)


@app.get("/login.css")
async def serve_login_css():
    """Serve login CSS file"""
    css_file = frontend_path / "login.css"
    if css_file.exists():
        response = HTMLResponse(content=css_file.read_text(encoding='utf-8'), media_type="text/css")
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response
    raise HTTPException(status_code=404, detail="login.css not found")


@app.get("/login.js")
async def serve_login_js():
    """Serve login JavaScript file"""
    js_file = frontend_path / "login.js"
    if js_file.exists():
        response = HTMLResponse(content=js_file.read_text(encoding='utf-8'), media_type="application/javascript")
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response
    raise HTTPException(status_code=404, detail="login.js not found")


@app.get("/script.js")
async def serve_js():
    """Serve JavaScript file with caching"""
    js_file = frontend_path / "script.js"
    if js_file.exists():
        response = HTMLResponse(content=js_file.read_text(encoding='utf-8'), media_type="application/javascript")
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response
    raise HTTPException(status_code=404, detail="script.js not found")


@app.get("/style.css")
async def serve_css():
    """Serve CSS file with caching"""
    css_file = frontend_path / "style.css"
    if css_file.exists():
        response = HTMLResponse(content=css_file.read_text(encoding='utf-8'), media_type="text/css")
        response.headers["Cache-Control"] = "public, max-age=3600"
        return response
    raise HTTPException(status_code=404, detail="style.css not found")


@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    except:
        gpu_available = False
        gpu_name = None
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "api": "online",
            "cache": {"status": "online", "items": cache.stats["items"]},
            "model": {"status": "ready", "device": "cuda" if gpu_available else "cpu", "gpu": gpu_name}
        }
    }


@app.get("/api/info")
async def api_info():
    """Get comprehensive API information"""
    return {
        "name": "Smart Financial Advisor",
        "version": "2.0.0",
        "description": "AI-powered stock prediction and portfolio optimization",
        "features": [
            "📈 Stock Price Prediction (LSTM Neural Network)",
            "📰 News Sentiment Analysis",
            "💼 Portfolio Optimization (Mean-Variance)",
            "⚠️ Risk Assessment (VaR, Volatility)",
            "📊 Technical Indicators (RSI, MACD, Bollinger Bands)"
        ],
        "endpoints": {
            "prediction": {"GET /api/predict/{symbol}": "Predict stock prices"},
            "sentiment": {"GET /api/sentiment/{symbol}": "Analyze sentiment"},
            "portfolio": {"POST /api/portfolio/optimize": "Optimize portfolio"}
        }
    }


@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {"cache": cache.stats, "ttl_seconds": cache.default_ttl}


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear the cache"""
    cache.clear()
    return {"message": "Cache cleared successfully"}


@app.get("/api/stocks/popular")
async def popular_stocks():
    """Get list of popular stocks"""
    return {
        "stocks": [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Automotive"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial"}
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
