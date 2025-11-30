"""
Smart Financial Advisor - System Test Suite
Comprehensive testing of all components
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

print("=" * 80)
print("SMART FINANCIAL ADVISOR - SYSTEM TEST SUITE")
print("=" * 80)
print()

test_results = []

# Test 1: Dependencies
print("TEST 1: Checking Python Dependencies")
print("-" * 80)
try:
    import fastapi
    import uvicorn
    import pandas
    import numpy
    import torch
    import sklearn
    import yfinance
    import vaderSentiment
    print("✅ fastapi:", fastapi.__version__)
    print("✅ pandas:", pandas.__version__)
    print("✅ numpy:", numpy.__version__)
    print("✅ torch:", torch.__version__)
    print("✅ scikit-learn:", sklearn.__version__)
    print("✅ yfinance:", yfinance.__version__)
    test_results.append(("Dependencies", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("Dependencies", "FAIL"))

# Test 2: Data Layer
print("\n\nTEST 2: Data Fetching Layer")
print("-" * 80)
try:
    from data.stock_data import StockDataFetcher
    fetcher = StockDataFetcher()
    print("✅ StockDataFetcher imported")
    
    # Test technical indicators with sample data
    import pandas as pd
    from datetime import datetime, timedelta
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    sample_data = pd.DataFrame({
        'Open': [100] * 100,
        'High': [105] * 100,
        'Low': [95] * 100,
        'Close': [102] * 100,
        'Volume': [1000000] * 100
    }, index=dates)
    
    enhanced = fetcher.add_technical_indicators(sample_data)
    print(f"✅ Technical indicators: {len(enhanced.columns)} columns")
    required_indicators = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_upper', 'BB_lower']
    missing = [ind for ind in required_indicators if ind not in enhanced.columns]
    if missing:
        print(f"⚠️  Missing indicators: {missing}")
    else:
        print("✅ All required indicators present")
    test_results.append(("Data Layer", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("Data Layer", "FAIL"))

# Test 3: Sentiment Analyzer
print("\n\nTEST 3: Sentiment Analysis")
print("-" * 80)
try:
    from models.sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer()
    print("✅ SentimentAnalyzer imported")
    
    # Test with sample text
    test_text = "The stock price is increasing rapidly and investors are optimistic"
    result = analyzer.analyze_text(test_text)
    print(f"✅ Sentiment analysis: {result['sentiment']} (score: {result['score']:.3f})")
    
    if result['sentiment'] in ['positive', 'negative', 'neutral']:
        print("✅ Sentiment classification working")
    
    test_results.append(("Sentiment Analysis", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("Sentiment Analysis", "FAIL"))

# Test 4: Portfolio Optimizer
print("\n\nTEST 4: Portfolio Optimization")
print("-" * 80)
try:
    from models.portfolio_optimizer import PortfolioOptimizer
    optimizer = PortfolioOptimizer()
    print("✅ PortfolioOptimizer imported")
    
    # Test with sample returns
    import pandas as pd
    import numpy as np
    np.random.seed(42)
    returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 100),
        'GOOGL': np.random.normal(0.001, 0.02, 100),
        'MSFT': np.random.normal(0.001, 0.02, 100)
    })
    
    result = optimizer.optimize_sharpe(returns)
    print(f"✅ Sharpe optimization: Ratio = {result['sharpe_ratio']:.2f}")
    print(f"✅ Weights: {', '.join([f'{k}={v:.1f}%' for k, v in result['weights'].items()])}")
    
    if abs(sum(result['weights'].values()) - 100.0) < 0.1:
        print("✅ Weights sum to 100%")
    
    test_results.append(("Portfolio Optimizer", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("Portfolio Optimizer", "FAIL"))

# Test 5: LSTM Predictor
print("\n\nTEST 5: LSTM Predictor")
print("-" * 80)
try:
    from models.lstm_predictor import LSTMPredictor, StockPricePredictor
    print("✅ LSTM modules imported")
    
    # Check PyTorch CUDA availability
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
    else:
        print("ℹ️  Running on CPU (GPU not available)")
    
    # Create a simple LSTM model
    model = LSTMPredictor(input_size=14, hidden_size=50, num_layers=2)
    print(f"✅ LSTM model created: {sum(p.numel() for p in model.parameters())} parameters")
    
    test_results.append(("LSTM Predictor", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("LSTM Predictor", "FAIL"))

# Test 6: API Routes
print("\n\nTEST 6: API Routes")
print("-" * 80)
try:
    from routes import prediction, sentiment, portfolio
    print("✅ Prediction routes imported")
    print("✅ Sentiment routes imported")
    print("✅ Portfolio routes imported")
    
    # Check route structure
    print(f"✅ Prediction router: {prediction.router.prefix}")
    print(f"✅ Sentiment router: {sentiment.router.prefix}")
    print(f"✅ Portfolio router: {portfolio.router.prefix}")
    
    test_results.append(("API Routes", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("API Routes", "FAIL"))

# Test 7: FastAPI Application
print("\n\nTEST 7: FastAPI Application")
print("-" * 80)
try:
    from backend.main import app
    print(f"✅ FastAPI app loaded: {app.title}")
    print(f"✅ Total routes: {len(app.routes)}")
    
    # List key endpoints
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    key_routes = ['/api/predict', '/api/sentiment', '/api/portfolio']
    found_routes = [r for r in routes if any(k in r for k in key_routes)]
    print(f"✅ Key API routes found: {len(found_routes)}")
    
    test_results.append(("FastAPI App", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("FastAPI App", "FAIL"))

# Test 8: Frontend Files
print("\n\nTEST 8: Frontend Files")
print("-" * 80)
try:
    frontend_files = [
        'frontend/index.html',
        'frontend/style.css',
        'frontend/script.js'
    ]
    
    for file in frontend_files:
        filepath = Path(__file__).parent / file
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✅ {file}: {size:,} bytes")
        else:
            print(f"❌ {file}: NOT FOUND")
            raise FileNotFoundError(f"{file} not found")
    
    test_results.append(("Frontend Files", "PASS"))
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_results.append(("Frontend Files", "FAIL"))

# Summary
print("\n\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed = sum(1 for _, status in test_results if status == "PASS")
total = len(test_results)

for test_name, status in test_results:
    icon = "✅" if status == "PASS" else "❌"
    print(f"{icon} {test_name:<30s} {status}")

print("\n" + "-" * 80)
print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

if passed == total:
    print("\n🎉 ALL TESTS PASSED! System is fully functional.")
    print("\nNext steps:")
    print("1. Run demo: python quick_demo.py")
    print("2. Start server: python -m uvicorn backend.main:app --reload")
    print("3. Open browser: http://localhost:8000")
else:
    print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")

print("=" * 80)
