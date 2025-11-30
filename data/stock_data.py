"""
Stock Data Fetching and Management
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetch and manage stock market data"""
    
    def __init__(self):
        self.cache = {}
    
    def fetch_stock_data(self, symbol: str, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch historical stock data"""
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                raise ValueError(f"No data found for {symbol}")
            
            logger.info(f"Fetched {len(df)} data points for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
    
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
        
        # Volatility (using standard deviation)
        df['Volatility'] = df['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
        
        # Price momentum
        df['Momentum'] = df['Close'] - df['Close'].shift(10)
        df['ROC'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # Drop NaN values
        df = df.dropna()
        
        logger.info(f"Added {len(df.columns) - 6} technical indicators")
        return df
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'marketCap': info.get('marketCap', 0),
                'currentPrice': info.get('currentPrice', 0),
                'dayHigh': info.get('dayHigh', 0),
                'dayLow': info.get('dayLow', 0),
                'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
                'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0),
                'volume': info.get('volume', 0),
                'averageVolume': info.get('averageVolume', 0),
                'beta': info.get('beta', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            }
        
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    def get_multiple_stocks(self, symbols: List[str], start_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple stocks"""
        results = {}
        
        for symbol in symbols:
            try:
                df = self.fetch_stock_data(symbol, start_date)
                df = self.add_technical_indicators(df)
                results[symbol] = df
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                results[symbol] = None
        
        return results


if __name__ == "__main__":
    # Test
    fetcher = StockDataFetcher()
    df = fetcher.fetch_stock_data("AAPL")
    df = fetcher.add_technical_indicators(df)
    print(f"Fetched {len(df)} rows with {len(df.columns)} columns")
    print(df.head())
