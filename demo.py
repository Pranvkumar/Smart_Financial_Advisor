"""
Smart Financial Advisor - Simple Demo Script
Demonstrates the key functionality without running the full server
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("SMART FINANCIAL ADVISOR - AI-POWERED STOCK ANALYSIS")
print("=" * 80)
print()

# Demo 1: Stock Data Fetching
print("\n📊 DEMO 1: Fetching Stock Data with Technical Indicators")
print("-" * 80)

try:
    from data.stock_data import StockDataFetcher
    
    fetcher = StockDataFetcher()
    symbol = "AAPL"
    
    print(f"\nFetching data for {symbol}...")
    # Fetch last 1 year of data
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    data = fetcher.fetch_stock_data(symbol, start_date=start_date, end_date=end_date)
    
    if data is not None:
        print(f"✅ Successfully fetched {len(data)} days of data")
        print(f"\nStock Info:")
        info = fetcher.get_stock_info(symbol)
        print(f"  Company: {info.get('name', 'N/A')}")
        print(f"  Market Cap: ${info.get('marketCap', 0):,.0f}")
        print(f"  P/E Ratio: {info.get('pe_ratio', 'N/A')}")
        print(f"  Beta: {info.get('beta', 'N/A')}")
        
        print(f"\nLatest data point:")
        latest = data.iloc[-1]
        print(f"  Date: {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"  Close: ${latest['Close']:.2f}")
        print(f"  Volume: {latest['Volume']:,.0f}")
        
        print(f"\nTechnical Indicators (latest):")
        print(f"  SMA_20: ${latest['SMA_20']:.2f}")
        print(f"  SMA_50: ${latest['SMA_50']:.2f}")
        print(f"  RSI: {latest['RSI']:.2f}")
        print(f"  MACD: {latest['MACD']:.4f}")
        print(f"  BB_upper: ${latest['BB_upper']:.2f}")
        print(f"  BB_lower: ${latest['BB_lower']:.2f}")
    else:
        print("❌ Failed to fetch data")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Demo 2: Sentiment Analysis
print("\n\n📰 DEMO 2: News Sentiment Analysis")
print("-" * 80)

try:
    from models.sentiment_analyzer import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer()
    symbol = "TSLA"
    
    print(f"\nAnalyzing sentiment for {symbol}...")
    result = analyzer.analyze_stock_sentiment(symbol, days=7)
    
    print(f"\n✅ Sentiment Analysis Results:")
    print(f"  Sentiment: {result['sentiment'].upper()}")
    print(f"  Score: {result['score']:.2f} (-1 = negative, 0 = neutral, +1 = positive)")
    print(f"  Confidence: {result['confidence']:.1%}")
    print(f"  Articles Analyzed: {result['articles_analyzed']}")
    print(f"    Positive: {result['positive_count']}")
    print(f"    Negative: {result['negative_count']}")
    print(f"    Neutral: {result['neutral_count']}")
    if result['articles_analyzed'] > 0:
        impact = analyzer.get_sentiment_impact(result['score'])
        print(f"  Impact: {impact}")
    
    print(f"\nTrading Signal:")
    signal = analyzer.get_sentiment_signal(result['score'], result['confidence'])
    print(f"  Action: {signal['action'].upper()}")
    print(f"  Strength: {signal['strength']}")
    print(f"  Reason: {signal['reason']}")
    
    if result['articles']:
        print(f"\nRecent News Headlines (showing top 3):")
        for i, article in enumerate(result['articles'][:3], 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     Source: {article['source']} | Sentiment: {article['sentiment']}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Demo 3: Portfolio Optimization
print("\n\n💼 DEMO 3: Portfolio Optimization")
print("-" * 80)

try:
    from models.portfolio_optimizer import PortfolioOptimizer
    
    optimizer = PortfolioOptimizer()
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    portfolio_value = 10000
    
    print(f"\nOptimizing portfolio for: {', '.join(symbols)}")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print("\nFetching historical data...")
    
    # Fetch data for all symbols
    from data.stock_data import StockDataFetcher
    from datetime import datetime, timedelta
    
    fetcher = StockDataFetcher()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    returns_data = {}
    for sym in symbols:
        data = fetcher.fetch_stock_data(sym, start_date=start_date, end_date=end_date)
        if data is not None:
            returns_data[sym] = data['Close'].pct_change().dropna()
    
    import pandas as pd
    returns_df = pd.DataFrame(returns_data)
    
    # Optimize portfolio
    result = optimizer.optimize_sharpe(returns_df)
    
    if result:
        print("\n✅ Optimization Complete!")
        
        print(f"\nOptimal Allocation (Maximum Sharpe Ratio):")
        for symbol, weight in result['weights'].items():
            amount = portfolio_value * (weight / 100)
            print(f"  {symbol}: {weight:.1f}% (${amount:,.2f})")
        
        print(f"\nPortfolio Metrics:")
        print(f"  Expected Annual Return: {result['expected_return']*100:.2f}%")
        print(f"  Annual Volatility (Risk): {result['volatility']*100:.2f}%")
        print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        
        # Calculate VaR
        var_95 = optimizer.calculate_var(returns_df, result['weights'], portfolio_value, confidence=0.95)
        var_99 = optimizer.calculate_var(returns_df, result['weights'], portfolio_value, confidence=0.99)
        diversification = optimizer.diversification_score(result['weights'])
        
        print(f"  Diversification Score: {diversification:.0f}/100")
        
        print(f"\nRisk Analysis:")
        print(f"  Value at Risk (95% confidence): ${var_95:,.2f}")
        print(f"  Value at Risk (99% confidence): ${var_99:,.2f}")
        print(f"  Interpretation: With 95% confidence, maximum 1-day loss should not exceed ${var_95:,.2f}")
    else:
        print("❌ Optimization failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n\n" + "=" * 80)
print("DEMO COMPLETE!")
print("=" * 80)
print("\nTo run the full web application:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Start server: cd backend && python main.py")
print("3. Open browser: http://localhost:8000")
print("\nFor more information, see README.md")
print("=" * 80)
