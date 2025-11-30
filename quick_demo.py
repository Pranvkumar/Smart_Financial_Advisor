"""
Smart Financial Advisor - Quick Demo
Shows the AI-powered financial analysis capabilities with sample data
"""

print("=" * 80)
print("SMART FINANCIAL ADVISOR - AI-POWERED STOCK ANALYSIS")
print("Quick Demonstration with Sample Data")
print("=" * 80)

# Demo 1: Portfolio Optimization with Sample Returns
print("\n\n💼 PORTFOLIO OPTIMIZATION DEMO")
print("-" * 80)
print("\nScenario: You have $10,000 to invest across 4 tech stocks")
print("Stocks: AAPL, GOOGL, MSFT, TSLA")
print("\nUsing Modern Portfolio Theory to find optimal allocation...")

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate sample daily returns (250 trading days)
np.random.seed(42)
dates = pd.date_range(end=datetime.now(), periods=250, freq='D')

# Simulate realistic returns for tech stocks
returns_data = {
    'AAPL': np.random.normal(0.001, 0.02, 250),   # Avg: 0.1% daily, Volatility: 2%
    'GOOGL': np.random.normal(0.0008, 0.025, 250), # Avg: 0.08% daily, Volatility: 2.5%
    'MSFT': np.random.normal(0.0009, 0.018, 250),  # Avg: 0.09% daily, Volatility: 1.8%
    'TSLA': np.random.normal(0.0015, 0.04, 250)    # Avg: 0.15% daily, Volatility: 4%
}

returns_df = pd.DataFrame(returns_data, index=dates)

print("\n📊 Historical Performance (annualized):")
for symbol in returns_df.columns:
    annual_return = returns_df[symbol].mean() * 252 * 100
    annual_vol = returns_df[symbol].std() * np.sqrt(252) * 100
    print(f"  {symbol}: Return={annual_return:6.2f}%, Volatility={annual_vol:6.2f}%")

# Calculate optimal portfolio
from models.portfolio_optimizer import PortfolioOptimizer

optimizer = PortfolioOptimizer()
result = optimizer.optimize_sharpe(returns_df)

portfolio_value = 10000

print("\n✅ OPTIMAL ALLOCATION (Maximum Sharpe Ratio):")
print("-" * 80)
for symbol, weight in result['weights'].items():
    amount = portfolio_value * (weight / 100)
    print(f"  {symbol:6s}: {weight:5.1f}% = ${amount:8,.2f}")

print(f"\n📈 PORTFOLIO METRICS:")
print("-" * 80)
print(f"  Expected Annual Return:  {result['expected_return']*100:6.2f}%")
print(f"  Annual Volatility (Risk): {result['volatility']*100:6.2f}%")
print(f"  Sharpe Ratio:            {result['sharpe_ratio']:6.2f}")

diversification = optimizer.diversification_score(result['weights'])
print(f"  Diversification Score:    {diversification:.0f}/100")

# Risk Analysis
# Convert percentage weights to decimal for VaR calculation
weights_array = np.array([result['weights'][symbol]/100 for symbol in returns_df.columns])
var_95 = optimizer.calculate_var(returns_df, weights_array, confidence=0.95, portfolio_value=portfolio_value)
var_99 = optimizer.calculate_var(returns_df, weights_array, confidence=0.99, portfolio_value=portfolio_value)

print(f"\n⚠️  RISK ANALYSIS:")
print("-" * 80)
print(f"  Value at Risk (95%): ${var_95:,.2f}")
print(f"  Value at Risk (99%): ${var_99:,.2f}")
print(f"\n  With 95% confidence, your maximum 1-day loss should not exceed ${var_95:,.2f}")
print(f"  There's only a 1% chance of losing more than ${var_99:,.2f} in a single day")

# Compare with equal-weight portfolio
equal_weights = {symbol: 25.0 for symbol in returns_df.columns}
equal_result = {
    'weights': equal_weights,
    'expected_return': (returns_df.mean() * equal_weights['AAPL']/100 * 252).sum(),
    'volatility': np.sqrt(252) * np.sqrt((returns_df.cov() @ np.array([0.25, 0.25, 0.25, 0.25])).dot(np.array([0.25, 0.25, 0.25, 0.25]))),
}
equal_result['sharpe_ratio'] = (equal_result['expected_return'] - 0.02) / equal_result['volatility']

print(f"\n📊 COMPARISON: Optimized vs Equal-Weight Portfolio")
print("-" * 80)
print(f"{'Metric':<25s} {'Equal-Weight':>15s} {'Optimized':>15s} {'Improvement':>15s}")
print("-" * 80)

opt_return = result['expected_return'] * 100
eq_return = equal_result['expected_return'] * 100
ret_diff = opt_return - eq_return

opt_vol = result['volatility'] * 100
eq_vol = equal_result['volatility'] * 100
vol_diff = eq_vol - opt_vol

opt_sharpe = result['sharpe_ratio']
eq_sharpe = equal_result['sharpe_ratio']
sharpe_diff = opt_sharpe - eq_sharpe

print(f"{'Expected Return':<25s} {eq_return:>14.2f}% {opt_return:>14.2f}% {ret_diff:>+14.2f}%")
print(f"{'Volatility':<25s} {eq_vol:>14.2f}% {opt_vol:>14.2f}% {vol_diff:>+14.2f}%")
print(f"{'Sharpe Ratio':<25s} {eq_sharpe:>15.2f} {opt_sharpe:>15.2f} {sharpe_diff:>+15.2f}")

# Demo 2: Sentiment Analysis
print("\n\n📰 SENTIMENT ANALYSIS DEMO")
print("-" * 80)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Sample news headlines
sample_news = [
    "Tesla delivers record number of vehicles, beating analyst expectations",
    "Apple announces groundbreaking new AI features in latest iPhone",
    "Microsoft cloud revenue surges 30% year-over-year",
    "Google faces regulatory scrutiny over antitrust concerns",
    "Tech stocks rally on positive earnings reports",
]

print("\nAnalyzing recent news headlines...")
print("\n" + "-" * 80)

sentiments = []
for i, headline in enumerate(sample_news, 1):
    score = analyzer.polarity_scores(headline)
    compound = score['compound']
    
    if compound >= 0.05:
        sentiment = 'POSITIVE'
        color = '🟢'
    elif compound <= -0.05:
        sentiment = 'NEGATIVE'
        color = '🔴'
    else:
        sentiment = 'NEUTRAL'
        color = '⚪'
    
    sentiments.append(compound)
    print(f"\n{i}. {headline}")
    print(f"   {color} {sentiment} (Score: {compound:+.3f})")

avg_sentiment = sum(sentiments) / len(sentiments)
positive_count = sum(1 for s in sentiments if s >= 0.05)
negative_count = sum(1 for s in sentiments if s <= -0.05)
neutral_count = len(sentiments) - positive_count - negative_count

print("\n" + "-" * 80)
print(f"\n📊 OVERALL SENTIMENT ANALYSIS:")
print(f"  Average Sentiment Score: {avg_sentiment:+.3f}")
print(f"  Positive Articles: {positive_count}")
print(f"  Negative Articles: {negative_count}")
print(f"  Neutral Articles: {neutral_count}")

if avg_sentiment >= 0.3:
    signal = "🟢 STRONG BUY"
    reason = "Very positive market sentiment"
elif avg_sentiment >= 0.05:
    signal = "🟢 BUY"
    reason = "Moderately positive sentiment"
elif avg_sentiment <= -0.3:
    signal = "🔴 STRONG SELL"
    reason = "Very negative market sentiment"
elif avg_sentiment <= -0.05:
    signal = "🔴 SELL"
    reason = "Moderately negative sentiment"
else:
    signal = "⚪ HOLD"
    reason = "Neutral sentiment, wait for clearer signals"

print(f"\n💡 TRADING SIGNAL: {signal}")
print(f"  Reason: {reason}")

# Demo 3: Technical Indicators
print("\n\n📈 TECHNICAL INDICATORS DEMO")
print("-" * 80)

print("\nGenerating sample stock price data...")

# Generate sample OHLCV data
dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
base_price = 150
prices = []
volumes = []

for i in range(200):
    # Random walk with slight upward trend
    change = np.random.normal(0.001, 0.02)
    base_price = base_price * (1 + change)
    prices.append(base_price)
    volumes.append(int(np.random.normal(50000000, 10000000)))

price_df = pd.DataFrame({
    'Close': prices,
    'Volume': volumes
}, index=dates)

# Calculate indicators
price_df['SMA_20'] = price_df['Close'].rolling(window=20).mean()
price_df['SMA_50'] = price_df['Close'].rolling(window=50).mean()
price_df['EMA_12'] = price_df['Close'].ewm(span=12).mean()
price_df['EMA_26'] = price_df['Close'].ewm(span=26).mean()
price_df['MACD'] = price_df['EMA_12'] - price_df['EMA_26']
price_df['Signal'] = price_df['MACD'].ewm(span=9).mean()

# RSI calculation
delta = price_df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
price_df['RSI'] = 100 - (100 / (1 + rs))

# Bollinger Bands
price_df['BB_middle'] = price_df['Close'].rolling(window=20).mean()
bb_std = price_df['Close'].rolling(window=20).std()
price_df['BB_upper'] = price_df['BB_middle'] + (bb_std * 2)
price_df['BB_lower'] = price_df['BB_middle'] - (bb_std * 2)

latest = price_df.iloc[-1]

print(f"\n📊 CURRENT PRICE AND INDICATORS (Latest Day):")
print("-" * 80)
print(f"  Current Price:     ${latest['Close']:.2f}")
print(f"  SMA 20-day:        ${latest['SMA_20']:.2f}")
print(f"  SMA 50-day:        ${latest['SMA_50']:.2f}")
print(f"  RSI (14):          {latest['RSI']:.2f}")
print(f"  MACD:              {latest['MACD']:.3f}")
print(f"  MACD Signal:       {latest['Signal']:.3f}")
print(f"  Bollinger Upper:   ${latest['BB_upper']:.2f}")
print(f"  Bollinger Lower:   ${latest['BB_lower']:.2f}")

# Generate trading signals
signals = []

if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
    signals.append("✅ Golden Cross Pattern - Bullish")
elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
    signals.append("⚠️ Death Cross Pattern - Bearish")

if latest['RSI'] > 70:
    signals.append("⚠️ RSI Overbought (>70) - Consider taking profits")
elif latest['RSI'] < 30:
    signals.append("✅ RSI Oversold (<30) - Potential buying opportunity")

if latest['MACD'] > latest['Signal']:
    signals.append("✅ MACD Bullish Crossover")
else:
    signals.append("⚠️ MACD Bearish Crossover")

if latest['Close'] > latest['BB_upper']:
    signals.append("⚠️ Price above upper Bollinger Band - Overbought")
elif latest['Close'] < latest['BB_lower']:
    signals.append("✅ Price below lower Bollinger Band - Oversold")

print(f"\n💡 TRADING SIGNALS:")
print("-" * 80)
for signal in signals:
    print(f"  {signal}")

# Summary
print("\n\n" + "=" * 80)
print("DEMO COMPLETE - KEY FEATURES DEMONSTRATED")
print("=" * 80)
print("""
✅ Portfolio Optimization using Modern Portfolio Theory
   - Maximum Sharpe Ratio optimization
   - Risk analysis with Value at Risk (VaR)
   - Diversification scoring
   
✅ Sentiment Analysis using VADER NLP
   - News headline analysis
   - Aggregate sentiment scoring
   - Trading signal generation
   
✅ Technical Indicators (20+ available)
   - Moving Averages (SMA, EMA)
   - RSI, MACD, Bollinger Bands
   - Volume and momentum indicators
   
✅ Machine Learning (LSTM Neural Network)
   - GPU-accelerated training with PyTorch
   - 30-day price prediction
   - Confidence intervals
   
This demo used sample data for demonstration.
The full application fetches real-time data from Yahoo Finance!

To see the complete web interface:
1. Install dependencies: pip install -r requirements.txt  
2. Start server: python -m uvicorn backend.main:app --reload
3. Open browser: http://localhost:8000

For more information, see README.md
""")
print("=" * 80)
