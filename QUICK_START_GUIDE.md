# 🚀 Smart Financial Advisor - Quick Start Guide

Get the system running in under 5 minutes!

---

## ⚡ Prerequisites

- **Python 3.11+** installed
- **pip** (Python package manager)
- **10 GB free disk space** (for dependencies)
- **Internet connection** (for stock data)

---

## 📦 Installation

### Step 1: Clone or Download
```bash
cd C:\Coding\Smart_Financial_Advisor
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages that will be installed:**
- FastAPI, uvicorn (web framework)
- pandas, numpy (data processing)
- PyTorch (deep learning)
- scikit-learn (machine learning)
- yfinance (stock data)
- vaderSentiment (NLP)

**Installation time:** ~5-10 minutes

---

## 🎬 Run the Demo

### Option A: Quick Demo (Recommended First)
```bash
python quick_demo.py
```

**What it shows:**
- ✅ Portfolio optimization ($10K across 4 stocks)
- ✅ Sentiment analysis (5 news headlines)
- ✅ Technical indicators (20+ calculated)
- ✅ Trading signals generated

**Runtime:** ~5 seconds  
**Output:** Console with formatted results

---

## 🌐 Run the Web Application

### Step 1: Start the Server
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Open Browser
```
http://localhost:8000
```

### Step 3: Use the Dashboard

#### Prediction Tab:
1. Enter stock symbol (e.g., **AAPL**)
2. Select prediction days (30)
3. Click "**Predict**"
4. View: Price chart, metrics, recommendation

#### Sentiment Tab:
1. Enter stock symbol (e.g., **TSLA**)
2. Click "**Analyze Sentiment**"
3. View: Sentiment score, news articles, trading signal

#### Portfolio Tab:
1. Enter symbols: **AAPL,GOOGL,MSFT,TSLA**
2. Select method: **Maximum Sharpe Ratio**
3. Enter value: **10000**
4. Click "**Optimize**"
5. View: Allocation chart, risk analysis, recommendations

---

## 🧪 Run System Tests

```bash
python test_system.py
```

**What it tests:**
- ✅ All dependencies (8 packages)
- ✅ Data fetching layer
- ✅ Sentiment analyzer
- ✅ Portfolio optimizer
- ✅ LSTM predictor
- ✅ API routes
- ✅ FastAPI app
- ✅ Frontend files

**Expected result:** 8/8 tests PASS

---

## 🔧 Configuration (Optional)

### For Enhanced Features:

Create `.env` file:
```env
NEWS_API_KEY=your_newsapi_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
```

**Note:** Application works **without** API keys using Yahoo Finance!

### Get API Keys (Free Tiers):
- **NewsAPI:** https://newsapi.org/ (100 req/day)
- **Alpha Vantage:** https://www.alphavantage.co/ (5 req/min)
- **Finnhub:** https://finnhub.io/ (60 calls/min)

---

## 📊 Sample Usage

### Example 1: Stock Prediction
```python
# Using the dashboard:
1. Go to http://localhost:8000
2. Enter "AAPL" in Prediction tab
3. Click "Predict"
4. See 30-day price forecast with confidence intervals
```

### Example 2: Portfolio Optimization
```python
# Using the dashboard:
1. Go to Portfolio tab
2. Enter: AAPL,GOOGL,MSFT,TSLA
3. Portfolio value: $10,000
4. Click "Optimize"
5. See optimal allocation percentages
```

### Example 3: Sentiment Analysis
```python
# Using the dashboard:
1. Go to Sentiment tab
2. Enter "TSLA"
3. Click "Analyze Sentiment"
4. See sentiment score and trading signal
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No data found for symbol"
**Possible causes:**
- Invalid stock symbol
- Yahoo Finance temporary issue
- Network connection problem

**Solution:**
- Verify symbol (e.g., AAPL, not Apple)
- Try again in a few moments
- Check internet connection

### Issue: Server won't start
**Check:**
```bash
python -c "from backend.main import app; print('OK')"
```

**If fails:**
```bash
pip install --upgrade fastapi uvicorn
```

### Issue: Slow predictions
**Causes:**
- First run (downloads data + trains model)
- Large prediction window (>60 days)
- No GPU available

**Solutions:**
- Wait for first run to complete
- Use smaller prediction windows
- Install CUDA for GPU acceleration

---

## 💡 Tips & Best Practices

### Performance:
- First prediction takes longer (trains model)
- Subsequent predictions are cached
- Use batch operations for multiple stocks

### Accuracy:
- More historical data = better predictions
- 2+ years of data recommended
- Technical indicators improve accuracy

### Data Sources:
- Yahoo Finance is free and reliable
- Updates daily after market close
- Real-time data requires paid APIs

---

## 📚 Documentation

- **README.md** - Full feature documentation
- **DEMO_SUMMARY.md** - Demo results and examples
- **SYSTEM_STATUS.md** - Complete system health report
- **API Docs** - http://localhost:8000/docs (when server running)

---

## 🎯 Next Steps

After getting it running:

1. **Customize:**
   - Adjust model parameters in `backend/simple_config.py`
   - Modify frontend styling in `frontend/style.css`
   - Add new indicators in `data/stock_data.py`

2. **Deploy:**
   - See deployment options in README.md
   - Docker support available
   - Deploy to AWS/GCP/Heroku

3. **Extend:**
   - Add backtesting module
   - Implement real-time updates
   - Create mobile app

---

## ✅ Verification

Run this to verify everything works:
```bash
python test_system.py && python quick_demo.py
```

**Expected output:**
```
✅ 8/8 tests passed (100.0%)
✅ Portfolio optimization demo
✅ Sentiment analysis demo
✅ Technical indicators demo
```

---

## 📞 Need Help?

**Author:** Pranvkumar Suhas Kshirsagar  
**Email:** pranavkshirsagar.409@gmail.com  
**GitHub:** [Pranvkumar/Smart_Financial_Advisor](https://github.com/Pranvkumar)

---

## 🎉 You're Ready!

The system is now running and fully functional. Start by running the demo, then explore the web dashboard!

**Happy Trading! 📈💰**
