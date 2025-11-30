"""
API Routes for Sentiment Analysis
"""
from fastapi import APIRouter, HTTPException, Query
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.sentiment_analyzer import SentimentAnalyzer
from backend.config import settings

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment"])

# Initialize sentiment analyzer
analyzer = SentimentAnalyzer(news_api_key=settings.NEWS_API_KEY)


@router.get("/{symbol}")
async def analyze_sentiment(
    symbol: str,
    days: int = Query(7, ge=1, le=30, description="Days of news to analyze")
):
    """
    Analyze sentiment for a stock from recent news
    
    - **symbol**: Stock ticker symbol
    - **days**: Number of days of news to analyze
    """
    try:
        result = analyzer.analyze_stock_sentiment(symbol, days)
        
        # Add impact assessment
        result['impact'] = analyzer.get_sentiment_impact(result['score'])
        
        # Add trading signal
        result['signal'] = get_sentiment_signal(result['score'], result['confidence'])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/{symbol}")
async def get_news(symbol: str, limit: int = Query(20, ge=1, le=100)):
    """Get recent news articles for a stock"""
    try:
        articles = analyzer.fetch_news(symbol, days=7)
        
        # Analyze each article
        analyzed = []
        for article in articles[:limit]:
            text = f"{article['title']} {article['description']}"
            sentiment = analyzer.analyze_text(text)
            analyzed.append({
                **article,
                'sentiment': sentiment['sentiment'],
                'sentiment_score': sentiment['score']
            })
        
        return {
            'symbol': symbol,
            'total_articles': len(analyzed),
            'articles': analyzed
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def analyze_multiple(symbols: list[str]):
    """Analyze sentiment for multiple stocks"""
    results = []
    
    for symbol in symbols:
        try:
            result = analyzer.analyze_stock_sentiment(symbol, days=7)
            result['impact'] = analyzer.get_sentiment_impact(result['score'])
            result['signal'] = get_sentiment_signal(result['score'], result['confidence'])
            results.append(result)
        except Exception as e:
            results.append({
                'symbol': symbol,
                'error': str(e)
            })
    
    return {'sentiments': results}


def get_sentiment_signal(score: float, confidence: float) -> dict:
    """Generate trading signal from sentiment"""
    if confidence < 0.5:
        return {'action': 'hold', 'strength': 'weak', 'reason': 'Low confidence in sentiment'}
    
    if score > 0.3:
        strength = 'strong' if score > 0.5 else 'moderate'
        return {'action': 'buy', 'strength': strength, 'reason': 'Positive market sentiment'}
    elif score < -0.3:
        strength = 'strong' if score < -0.5 else 'moderate'
        return {'action': 'sell', 'strength': strength, 'reason': 'Negative market sentiment'}
    else:
        return {'action': 'hold', 'strength': 'neutral', 'reason': 'Neutral sentiment'}
