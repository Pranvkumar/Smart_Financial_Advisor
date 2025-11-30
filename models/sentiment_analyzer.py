"""
Sentiment Analysis for Financial News and Social Media
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment from financial news and social media"""
    
    def __init__(self, news_api_key: str = None):
        self.vader = SentimentIntensityAnalyzer()
        self.news_api_key = news_api_key
        
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of a single text"""
        scores = self.vader.polarity_scores(text)
        
        # Determine overall sentiment
        if scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'text': text[:200],  # First 200 chars
            'sentiment': sentiment,
            'score': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    
    def fetch_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """Fetch news articles for a stock symbol"""
        news_articles = []
        
        try:
            # Try News API if key is provided
            if self.news_api_key:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': symbol,
                    'apiKey': self.news_api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'from': (datetime.now() - timedelta(days=days)).isoformat()
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    articles = response.json().get('articles', [])
                    for article in articles[:20]:  # Limit to 20 articles
                        news_articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('publishedAt', '')
                        })
            
            # Fallback: scrape Yahoo Finance (basic approach)
            if not news_articles:
                news_articles = self._scrape_yahoo_finance(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
        
        return news_articles
    
    def _scrape_yahoo_finance(self, symbol: str) -> List[Dict]:
        """Scrape news from Yahoo Finance (fallback)"""
        news_articles = []
        
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}/news"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # This is a simplified scraper - Yahoo's structure may change
                articles = soup.find_all('h3', limit=10)
                for article in articles:
                    title = article.get_text(strip=True)
                    if title:
                        news_articles.append({
                            'title': title,
                            'description': '',
                            'source': 'Yahoo Finance',
                            'url': '',
                            'published_at': datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.warning(f"Error scraping Yahoo Finance: {e}")
        
        return news_articles
    
    def analyze_stock_sentiment(self, symbol: str, days: int = 7) -> Dict:
        """Analyze overall sentiment for a stock"""
        # Fetch news
        news_articles = self.fetch_news(symbol, days)
        
        if not news_articles:
            return {
                'symbol': symbol,
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'articles_analyzed': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'articles': []
            }
        
        # Analyze each article
        analyzed_articles = []
        sentiment_scores = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in news_articles:
            text = f"{article['title']} {article['description']}"
            sentiment_result = self.analyze_text(text)
            
            sentiment_counts[sentiment_result['sentiment']] += 1
            sentiment_scores.append(sentiment_result['score'])
            
            analyzed_articles.append({
                **article,
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score']
            })
        
        # Calculate overall sentiment
        avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if avg_score >= 0.05:
            overall_sentiment = 'positive'
        elif avg_score <= -0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Calculate confidence based on consistency
        max_count = max(sentiment_counts.values())
        confidence = max_count / len(news_articles) if news_articles else 0
        
        return {
            'symbol': symbol,
            'sentiment': overall_sentiment,
            'score': round(avg_score, 3),
            'confidence': round(confidence, 2),
            'articles_analyzed': len(news_articles),
            'positive_count': sentiment_counts['positive'],
            'negative_count': sentiment_counts['negative'],
            'neutral_count': sentiment_counts['neutral'],
            'articles': analyzed_articles[:10],  # Return top 10
            'analysis_date': datetime.now().isoformat()
        }
    
    def get_sentiment_impact(self, sentiment_score: float) -> str:
        """Get human-readable sentiment impact"""
        if sentiment_score >= 0.5:
            return "Strongly Positive - High buying pressure expected"
        elif sentiment_score >= 0.2:
            return "Positive - Moderate buying interest"
        elif sentiment_score >= 0.05:
            return "Slightly Positive - Mild bullish sentiment"
        elif sentiment_score >= -0.05:
            return "Neutral - No clear market direction"
        elif sentiment_score >= -0.2:
            return "Slightly Negative - Mild bearish sentiment"
        elif sentiment_score >= -0.5:
            return "Negative - Moderate selling pressure"
        else:
            return "Strongly Negative - High selling pressure expected"


if __name__ == "__main__":
    # Test
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_stock_sentiment("AAPL")
    print(f"Sentiment for AAPL: {result['sentiment']} ({result['score']})")
    print(f"Analyzed {result['articles_analyzed']} articles")
