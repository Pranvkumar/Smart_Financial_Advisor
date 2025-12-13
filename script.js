/**
 * Smart Financial Advisor - Frontend JavaScript
 * Professional UI with 3D Effects and Animations
 */

// ============================================
// Global Variables & Configuration
// ============================================
const API_BASE = 'http://localhost:8000/api';
let predictionChart = null;
let allocationChart = null;

// ============================================
// DOM Elements
// ============================================
const elements = {
    // Navigation
    navTabs: document.querySelectorAll('.nav-tab'),
    tabPanels: document.querySelectorAll('.tab-panel'),
    
    // Prediction Tab
    stockSymbol: document.getElementById('stockSymbol'),
    predictionDays: document.getElementById('predictionDays'),
    predictBtn: document.getElementById('predictBtn'),
    predictionResults: document.getElementById('predictionResults'),
    
    // Sentiment Tab
    sentimentSymbol: document.getElementById('sentimentSymbol'),
    analyzeSentimentBtn: document.getElementById('analyzeSentimentBtn'),
    sentimentResults: document.getElementById('sentimentResults'),
    
    // Portfolio Tab
    portfolioSymbols: document.getElementById('portfolioSymbols'),
    portfolioValue: document.getElementById('portfolioValue'),
    optimizeBtn: document.getElementById('optimizeBtn'),
    portfolioResults: document.getElementById('portfolioResults'),
    
    // Loading & Toast
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer')
};

// ============================================
// Utility Functions
// ============================================
function showLoading() {
    elements.loadingOverlay.classList.add('active');
}

function hideLoading() {
    elements.loadingOverlay.classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <span style="font-size: 1.25rem;">${icons[type]}</span>
        <span>${message}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatPercent(value) {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
}

// ============================================
// Navigation
// ============================================
function initNavigation() {
    elements.navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;
            
            // Update active tab
            elements.navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active panel
            elements.tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `${targetId}-tab`) {
                    panel.classList.add('active');
                }
            });
        });
    });
}

// ============================================
// Quick Pick Chips
// ============================================
function initChips() {
    // Stock symbol chips
    document.querySelectorAll('.chip[data-symbol]').forEach(chip => {
        chip.addEventListener('click', () => {
            elements.stockSymbol.value = chip.dataset.symbol;
            elements.stockSymbol.focus();
        });
    });
    
    // Portfolio template chips
    document.querySelectorAll('.chip[data-symbols]').forEach(chip => {
        chip.addEventListener('click', () => {
            elements.portfolioSymbols.value = chip.dataset.symbols;
            elements.portfolioSymbols.focus();
        });
    });
}

// ============================================
// Prediction Functions
// ============================================
async function getPrediction() {
    const symbol = elements.stockSymbol.value.trim().toUpperCase();
    const days = parseInt(elements.predictionDays.value) || 30;
    
    if (!symbol) {
        showToast('Please enter a stock symbol', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, days })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        displayPredictionResults(data);
        showToast('Prediction complete!', 'success');
        
    } catch (error) {
        console.error('Prediction error:', error);
        // Generate mock data for demo
        const mockData = generateMockPrediction(symbol, days);
        displayPredictionResults(mockData);
        showToast('Using demo data (API unavailable)', 'warning');
    } finally {
        hideLoading();
    }
}

function generateMockPrediction(symbol, days) {
    const basePrice = 150 + Math.random() * 100;
    const change = (Math.random() - 0.4) * 20;
    const targetPrice = basePrice * (1 + change / 100);
    
    const historical = [];
    const predictions = [];
    
    // Generate historical data
    let price = basePrice * 0.9;
    for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        price += (Math.random() - 0.48) * 3;
        historical.push({
            date: date.toISOString().split('T')[0],
            price: Math.max(price, basePrice * 0.7)
        });
    }
    
    // Generate predictions
    price = historical[historical.length - 1].price;
    for (let i = 1; i <= days; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i);
        price += (Math.random() - 0.45) * 2;
        predictions.push({
            date: date.toISOString().split('T')[0],
            price: Math.max(price, basePrice * 0.7)
        });
    }
    
    return {
        symbol,
        name: getCompanyName(symbol),
        exchange: 'NASDAQ',
        current_price: basePrice,
        predicted_price: targetPrice,
        expected_change: change,
        confidence: 75 + Math.random() * 20,
        recommendation: change > 5 ? 'Buy' : change < -5 ? 'Sell' : 'Hold',
        historical_data: historical,
        predictions: predictions,
        indicators: {
            rsi: 30 + Math.random() * 40,
            macd: (Math.random() - 0.5) * 5,
            sma_20: basePrice * (0.95 + Math.random() * 0.1),
            sma_50: basePrice * (0.9 + Math.random() * 0.15)
        },
        metrics: {
            rmse: 2 + Math.random() * 5,
            mae: 1.5 + Math.random() * 4,
            r2: 0.75 + Math.random() * 0.2
        }
    };
}

function getCompanyName(symbol) {
    const names = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'TSLA': 'Tesla Inc.',
        'MSFT': 'Microsoft Corp.',
        'NVDA': 'NVIDIA Corp.',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'JPM': 'JPMorgan Chase & Co.',
        'BAC': 'Bank of America Corp.',
        'GS': 'Goldman Sachs Group',
        'MS': 'Morgan Stanley',
        'JNJ': 'Johnson & Johnson',
        'PFE': 'Pfizer Inc.',
        'UNH': 'UnitedHealth Group',
        'ABBV': 'AbbVie Inc.'
    };
    return names[symbol] || `${symbol} Corporation`;
}

function displayPredictionResults(data) {
    elements.predictionResults.style.display = 'grid';
    
    // Update stock info
    document.getElementById('stockName').textContent = data.name || data.symbol;
    document.getElementById('stockExchange').textContent = data.exchange || 'NYSE';
    document.getElementById('currentPrice').textContent = formatCurrency(data.current_price);
    
    const priceChangeEl = document.getElementById('priceChange');
    const changeVal = data.expected_change || 0;
    priceChangeEl.textContent = formatPercent(changeVal);
    priceChangeEl.className = `price-change ${changeVal >= 0 ? 'positive' : 'negative'}`;
    
    // Update prediction stats
    document.getElementById('targetPrice').textContent = formatCurrency(data.predicted_price);
    
    const expectedChangeEl = document.getElementById('expectedChange');
    expectedChangeEl.textContent = formatPercent(data.expected_change);
    expectedChangeEl.className = `stat-value ${data.expected_change >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('confidence').textContent = `${Math.round(data.confidence)}%`;
    
    const recEl = document.getElementById('recommendation');
    const rec = data.recommendation?.toLowerCase() || 'hold';
    recEl.textContent = data.recommendation;
    recEl.className = `stat-value recommendation ${rec}`;
    
    // Update indicators
    if (data.indicators) {
        const rsi = data.indicators.rsi || 50;
        document.getElementById('rsiValue').textContent = Math.round(rsi);
        document.getElementById('rsiBar').style.width = `${rsi}%`;
        document.getElementById('macdValue').textContent = (data.indicators.macd || 0).toFixed(2);
        document.getElementById('sma20').textContent = formatCurrency(data.indicators.sma_20 || 0);
        document.getElementById('sma50').textContent = formatCurrency(data.indicators.sma_50 || 0);
    }
    
    // Update model metrics
    if (data.metrics) {
        document.getElementById('rmse').textContent = (data.metrics.rmse || 0).toFixed(2);
        document.getElementById('mae').textContent = (data.metrics.mae || 0).toFixed(2);
        document.getElementById('r2').textContent = (data.metrics.r2 || 0).toFixed(2);
    }
    
    // Update chart
    updatePredictionChart(data);
    
    // Smooth scroll to results
    elements.predictionResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updatePredictionChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    // Destroy existing chart
    if (predictionChart) {
        predictionChart.destroy();
    }
    
    const historical = data.historical_data || [];
    const predictions = data.predictions || [];
    
    const historicalLabels = historical.map(d => d.date);
    const historicalPrices = historical.map(d => d.price);
    const predictionLabels = predictions.map(d => d.date);
    const predictionPrices = predictions.map(d => d.price);
    
    const allLabels = [...historicalLabels, ...predictionLabels];
    const historicalData = [...historicalPrices, ...Array(predictionLabels.length).fill(null)];
    const predictionData = [...Array(historicalLabels.length - 1).fill(null), historicalPrices[historicalPrices.length - 1], ...predictionPrices];
    
    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allLabels,
            datasets: [
                {
                    label: 'Historical Price',
                    data: historicalData,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                },
                {
                    label: 'Predicted Price',
                    data: predictionData,
                    borderColor: '#22d3ee',
                    backgroundColor: 'rgba(34, 211, 238, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 15, 25, 0.9)',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    titleColor: '#fff',
                    bodyColor: 'rgba(255, 255, 255, 0.8)',
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                        maxTicksLimit: 8
                    }
                },
                y: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.5)',
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

// ============================================
// Sentiment Functions
// ============================================
async function analyzeSentiment() {
    const symbol = elements.sentimentSymbol.value.trim().toUpperCase();
    
    if (!symbol) {
        showToast('Please enter a stock symbol', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/sentiment/${symbol}`);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        displaySentimentResults(data);
        showToast('Sentiment analysis complete!', 'success');
        
    } catch (error) {
        console.error('Sentiment error:', error);
        // Generate mock data
        const mockData = generateMockSentiment(symbol);
        displaySentimentResults(mockData);
        showToast('Using demo data (API unavailable)', 'warning');
    } finally {
        hideLoading();
    }
}

function generateMockSentiment(symbol) {
    const score = (Math.random() - 0.5) * 2;
    const sentiment = score > 0.2 ? 'positive' : score < -0.2 ? 'negative' : 'neutral';
    
    return {
        symbol,
        overall_sentiment: sentiment,
        sentiment_score: score,
        confidence: 70 + Math.random() * 25,
        article_count: Math.floor(15 + Math.random() * 30),
        sources: Math.floor(3 + Math.random() * 5),
        trading_signal: score > 0.3 ? 'Buy' : score < -0.3 ? 'Sell' : 'Hold',
        news: [
            {
                title: `${symbol} Reports Strong Quarterly Earnings`,
                source: 'Financial Times',
                date: new Date().toISOString().split('T')[0],
                sentiment: 'positive',
                url: '#'
            },
            {
                title: `Analysts Upgrade ${symbol} Price Target`,
                source: 'Bloomberg',
                date: new Date().toISOString().split('T')[0],
                sentiment: 'positive',
                url: '#'
            },
            {
                title: `${symbol} Announces New Product Launch`,
                source: 'Reuters',
                date: new Date(Date.now() - 86400000).toISOString().split('T')[0],
                sentiment: 'neutral',
                url: '#'
            },
            {
                title: `Market Watch: ${symbol} Trading Analysis`,
                source: 'MarketWatch',
                date: new Date(Date.now() - 172800000).toISOString().split('T')[0],
                sentiment: 'neutral',
                url: '#'
            }
        ]
    };
}

function displaySentimentResults(data) {
    elements.sentimentResults.style.display = 'grid';
    
    const score = data.sentiment_score || 0;
    const sentiment = data.overall_sentiment || 'neutral';
    
    // Update sentiment circle
    const circle = document.getElementById('sentimentCircle');
    circle.className = `sentiment-circle ${sentiment}`;
    
    document.getElementById('sentimentScore').textContent = score.toFixed(2);
    document.getElementById('sentimentLabel').textContent = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
    
    // Update stats
    document.getElementById('articleCount').textContent = data.article_count || 0;
    document.getElementById('sentimentConfidence').textContent = `${Math.round(data.confidence || 0)}%`;
    document.getElementById('sentimentSignal').textContent = data.trading_signal || 'Hold';
    document.getElementById('sentimentSources').textContent = data.sources || 0;
    
    // Update news list
    const newsList = document.getElementById('newsList');
    newsList.innerHTML = '';
    
    if (data.news && data.news.length > 0) {
        data.news.forEach(item => {
            const newsItem = document.createElement('div');
            newsItem.className = 'news-item';
            newsItem.innerHTML = `
                <h4><a href="${item.url}" target="_blank">${item.title}</a></h4>
                <div class="news-meta">
                    <span>${item.source} • ${item.date}</span>
                    <span class="news-sentiment ${item.sentiment}">${item.sentiment}</span>
                </div>
            `;
            newsList.appendChild(newsItem);
        });
    } else {
        newsList.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">No news available</p>';
    }
    
    elements.sentimentResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================
// Portfolio Functions
// ============================================
async function optimizePortfolio() {
    const symbolsStr = elements.portfolioSymbols.value.trim().toUpperCase();
    const investment = parseFloat(elements.portfolioValue.value) || 100000;
    
    if (!symbolsStr) {
        showToast('Please enter stock symbols', 'warning');
        return;
    }
    
    const symbols = symbolsStr.split(',').map(s => s.trim()).filter(s => s);
    
    if (symbols.length < 2) {
        showToast('Please enter at least 2 symbols', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/portfolio/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbols, investment })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        displayPortfolioResults(data, symbols, investment);
        showToast('Portfolio optimized!', 'success');
        
    } catch (error) {
        console.error('Portfolio error:', error);
        // Generate mock data
        const mockData = generateMockPortfolio(symbols, investment);
        displayPortfolioResults(mockData, symbols, investment);
        showToast('Using demo data (API unavailable)', 'warning');
    } finally {
        hideLoading();
    }
}

function generateMockPortfolio(symbols, investment) {
    const weights = {};
    let remaining = 1;
    
    symbols.forEach((symbol, index) => {
        if (index === symbols.length - 1) {
            weights[symbol] = remaining;
        } else {
            const w = Math.random() * remaining * 0.6;
            weights[symbol] = w;
            remaining -= w;
        }
    });
    
    return {
        expected_return: 8 + Math.random() * 12,
        volatility: 12 + Math.random() * 15,
        sharpe_ratio: 0.8 + Math.random() * 0.8,
        var_95: -investment * (0.03 + Math.random() * 0.04),
        var_99: -investment * (0.05 + Math.random() * 0.06),
        diversification_score: 60 + Math.random() * 35,
        weights: weights,
        recommendations: [
            {
                type: 'rebalance',
                message: `Consider <strong>rebalancing</strong> your portfolio quarterly to maintain optimal allocation`
            },
            {
                type: 'diversify',
                message: `Add <strong>international exposure</strong> to reduce domestic market risk`
            },
            {
                type: 'risk',
                message: `Current <strong>Sharpe ratio</strong> suggests good risk-adjusted returns`
            }
        ]
    };
}

function displayPortfolioResults(data, symbols, investment) {
    elements.portfolioResults.style.display = 'grid';
    
    // Update metrics
    const expReturn = document.getElementById('expReturn');
    expReturn.textContent = formatPercent(data.expected_return);
    expReturn.className = `metric-value ${data.expected_return >= 0 ? 'positive' : 'negative'}`;
    
    document.getElementById('volatility').textContent = `${(data.volatility || 0).toFixed(1)}%`;
    document.getElementById('sharpeRatio').textContent = (data.sharpe_ratio || 0).toFixed(2);
    
    // Update risk metrics
    document.getElementById('var95').textContent = formatCurrency(data.var_95 || 0);
    document.getElementById('var99').textContent = formatCurrency(data.var_99 || 0);
    document.getElementById('diversification').textContent = `${Math.round(data.diversification_score || 0)}%`;
    
    // Update allocation chart and list
    updateAllocationChart(data.weights, symbols, investment);
    
    // Update recommendations
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = '';
    
    if (data.recommendations) {
        data.recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.innerHTML = `
                <div class="recommendation-text">${rec.message}</div>
            `;
            recList.appendChild(item);
        });
    }
    
    elements.portfolioResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateAllocationChart(weights, symbols, investment) {
    const ctx = document.getElementById('allocationChart').getContext('2d');
    
    if (allocationChart) {
        allocationChart.destroy();
    }
    
    const colors = [
        '#6366f1', '#22d3ee', '#8b5cf6', '#10b981', 
        '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'
    ];
    
    const data = symbols.map((symbol, index) => ({
        symbol,
        weight: weights[symbol] || 0,
        color: colors[index % colors.length]
    }));
    
    allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.symbol),
            datasets: [{
                data: data.map(d => (d.weight * 100).toFixed(1)),
                backgroundColor: data.map(d => d.color),
                borderColor: 'rgba(10, 10, 15, 0.8)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 15, 25, 0.9)',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    titleColor: '#fff',
                    bodyColor: 'rgba(255, 255, 255, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const value = investment * (context.parsed / 100);
                            return `${context.label}: ${context.parsed}% (${formatCurrency(value)})`;
                        }
                    }
                }
            }
        }
    });
    
    // Update allocation list
    const list = document.getElementById('allocationList');
    list.innerHTML = '';
    
    data.forEach(item => {
        const value = investment * item.weight;
        const el = document.createElement('div');
        el.className = 'allocation-item';
        el.innerHTML = `
            <div class="allocation-color" style="background: ${item.color}"></div>
            <span class="allocation-symbol">${item.symbol}</span>
            <span class="allocation-percent">${(item.weight * 100).toFixed(1)}%</span>
            <span class="allocation-value">${formatCurrency(value)}</span>
        `;
        list.appendChild(el);
    });
}

// ============================================
// Event Listeners
// ============================================
function initEventListeners() {
    // Prediction
    elements.predictBtn.addEventListener('click', getPrediction);
    elements.stockSymbol.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') getPrediction();
    });
    
    // Sentiment
    elements.analyzeSentimentBtn.addEventListener('click', analyzeSentiment);
    elements.sentimentSymbol.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeSentiment();
    });
    
    // Portfolio
    elements.optimizeBtn.addEventListener('click', optimizePortfolio);
    elements.portfolioSymbols.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') optimizePortfolio();
    });
}

// ============================================
// 3D Card Effects
// ============================================
function init3DEffects() {
    const cards = document.querySelectorAll('.card, .hero-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
}

// ============================================
// Initialize Application
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Smart Financial Advisor initialized');
    
    initNavigation();
    initChips();
    initEventListeners();
    
    // Add slight delay for 3D effects (after cards are rendered)
    setTimeout(init3DEffects, 500);
    
    // Add entrance animation
    document.body.style.opacity = '0';
    requestAnimationFrame(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    });
});
