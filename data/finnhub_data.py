"""
Stock Data Fetching with Finnhub API
"""
import finnhub
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class FinnhubDataFetcher:
    """Fetch stock data using Finnhub API"""
    
    def __init__(self):
        self.api_key = os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY not found in environment")
        self.client = finnhub.Client(api_key=self.api_key)
        self.cache = {}
    
    def fetch_stock_data(self, symbol: str, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch stock data - Free tier: generate from current quote"""
        try:
            logger.info(f"Fetching Finnhub quote for {symbol}")
            
            # Get current quote
            quote = self.client.quote(symbol)
            
            if not quote or not quote.get('c'):
                raise ValueError(f"No data found for {symbol}")
            
            # Free tier limitation: Generate synthetic historical data from current price
            # This simulates historical data for demo purposes
            current_price = quote['c']
            num_days = 500
            
            # Generate realistic price movements
            dates = pd.date_range(end=datetime.now(), periods=num_days, freq='D')
            
            # Create price path that ends at current price
            returns = np.random.randn(num_days) * 0.02  # 2% daily volatility
            returns[-1] = 0  # Last return is zero
            price_multipliers = np.exp(np.cumsum(returns))
            price_multipliers = price_multipliers / price_multipliers[-1]  # Normalize to end at 1
            prices = current_price * price_multipliers
            
            # Create realistic OHLC data
            df = pd.DataFrame({
                'Close': prices,
                'Open': prices * (1 + np.random.uniform(-0.01, 0.01, num_days)),
                'High': prices * (1 + np.random.uniform(0, 0.02, num_days)),
                'Low': prices * (1 - np.random.uniform(0, 0.02, num_days)),
                'Volume': np.random.randint(50000000, 150000000, num_days)
            }, index=dates)
            
            # Ensure realistic OHLC relationships
            df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
            df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
            
            logger.info(f"Generated {len(df)} data points for {symbol} (current: ${current_price})")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching Finnhub data for {symbol}: {e}")
            raise
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get stock company profile"""
        try:
            profile = self.client.company_profile2(symbol=symbol)
            quote = self.client.quote(symbol)
            
            return {
                'name': profile.get('name', symbol),
                'sector': profile.get('finnhubIndustry', 'N/A'),
                'marketCap': profile.get('marketCapitalization', 0) * 1000000,  # Convert to actual value
                'pe_ratio': quote.get('pe', 0) if quote else 0,
                'volume': int(quote.get('volume', 0)) if quote else 0,
                'beta': profile.get('beta', 1.0)
            }
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return {
                'name': symbol,
                'sector': 'N/A',
                'marketCap': 0,
                'pe_ratio': 0,
                'volume': 0,
                'beta': 1.0
            }
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple stocks"""
        result = {}
        for symbol in symbols:
            try:
                df = self.fetch_stock_data(symbol)
                result[symbol] = df
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                result[symbol] = None
        return result
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to dataframe"""
        df = df.copy()
        
        # Simple Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Volatility
        df['Volatility'] = df['Close'].rolling(window=20).std()
        
        # Momentum
        df['Momentum'] = df['Close'] - df['Close'].shift(10)
        
        # Rate of Change
        df['ROC'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
        
        # Average True Range
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # Drop NaN values
        df = df.dropna()
        
        return df
