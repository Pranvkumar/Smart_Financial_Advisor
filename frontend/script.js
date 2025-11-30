// Smart Financial Advisor - Frontend JavaScript

const API_BASE_URL = 'http://localhost:8000';

// Tab Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Update active button
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Show corresponding tab
        const tabName = btn.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Prediction Tab
document.getElementById('predictBtn').addEventListener('click', async () => {
    const symbol = document.getElementById('stockSymbol').value.toUpperCase().trim();
    const days = parseInt(document.getElementById('predictionDays').value);
    
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/predict/${symbol}?days=${days}`);
        const data = await response.json();
        
        if (response.ok) {
            displayPredictionResults(data);
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
});

function displayPredictionResults(data) {
    // Show results section
    document.getElementById('predictionResults').style.display = 'block';
    
    // Stock Info
    document.getElementById('stockName').textContent = data.stock_info.name;
    document.getElementById('stockSymbolDisplay').textContent = data.symbol;
    document.getElementById('currentPrice').textContent = `$${data.current_price}`;
    document.getElementById('marketCap').textContent = formatNumber(data.stock_info.marketCap);
    document.getElementById('peRatio').textContent = data.stock_info.pe_ratio.toFixed(2);
    document.getElementById('volume').textContent = formatNumber(data.stock_info.volume);
    document.getElementById('beta').textContent = data.stock_info.beta.toFixed(2);
    
    // Prediction Summary
    document.getElementById('predictedPrice').textContent = `$${data.summary.predicted_price}`;
    document.getElementById('priceChange').textContent = 
        `$${data.summary.price_change} (${data.summary.price_change_percent}%)`;
    
    const directionBadge = document.getElementById('direction');
    directionBadge.textContent = data.summary.direction.toUpperCase();
    directionBadge.className = `badge ${data.summary.direction}`;
    
    const recBadge = document.getElementById('recommendation');
    recBadge.textContent = data.summary.recommendation;
    recBadge.className = `badge ${data.summary.direction}`;
    
    // Model Metrics
    if (data.model_metrics) {
        document.getElementById('metricsCard').style.display = 'block';
        document.getElementById('testRmse').textContent = data.model_metrics.test_rmse.toFixed(2);
        document.getElementById('testMae').textContent = data.model_metrics.test_mae.toFixed(2);
        document.getElementById('r2Score').textContent = data.model_metrics.test_r2.toFixed(4);
    }
    
    // Draw Chart
    drawPredictionChart(data);
    
    // Scroll to results
    document.getElementById('predictionResults').scrollIntoView({ behavior: 'smooth' });
}

function drawPredictionChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    
    // Destroy previous chart if exists
    if (window.predictionChart) {
        window.predictionChart.destroy();
    }
    
    // Prepare data
    const historicalDates = data.historical_data.dates;
    const historicalPrices = data.historical_data.prices;
    
    const futureDates = [];
    const lastDate = new Date(historicalDates[historicalDates.length - 1]);
    for (let i = 1; i <= data.prediction_days; i++) {
        const date = new Date(lastDate);
        date.setDate(date.getDate() + i);
        futureDates.push(date.toISOString().split('T')[0]);
    }
    
    const allDates = [...historicalDates, ...futureDates];
    const allPrices = [...historicalPrices, ...Array(data.prediction_days).fill(null)];
    const predictions = [...Array(historicalDates.length).fill(null), ...data.predictions.prices];
    const upperBound = [...Array(historicalDates.length).fill(null), ...data.predictions.upper_bound];
    const lowerBound = [...Array(historicalDates.length).fill(null), ...data.predictions.lower_bound];
    
    window.predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: [
                {
                    label: 'Historical Price',
                    data: allPrices,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: 'Predicted Price',
                    data: predictions,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0
                },
                {
                    label: 'Upper Bound',
                    data: upperBound,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.05)',
                    borderWidth: 1,
                    fill: '+1',
                    pointRadius: 0
                },
                {
                    label: 'Lower Bound',
                    data: lowerBound,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.05)',
                    borderWidth: 1,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Sentiment Tab
document.getElementById('analyzeSentimentBtn').addEventListener('click', async () => {
    const symbol = document.getElementById('sentimentSymbol').value.toUpperCase().trim();
    
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/sentiment/${symbol}`);
        const data = await response.json();
        
        if (response.ok) {
            displaySentimentResults(data);
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
});

function displaySentimentResults(data) {
    document.getElementById('sentimentResults').style.display = 'block';
    
    // Sentiment Score
    const scoreCircle = document.getElementById('sentimentCircle');
    scoreCircle.className = `score-circle ${data.sentiment}`;
    document.getElementById('sentimentScore').textContent = data.score.toFixed(2);
    document.getElementById('sentimentLabel').textContent = data.sentiment.toUpperCase();
    
    // Details
    document.getElementById('sentimentConfidence').style.width = `${data.confidence * 100}%`;
    document.getElementById('articlesAnalyzed').textContent = data.articles_analyzed;
    document.getElementById('sentimentImpact').textContent = data.impact;
    
    const signalBadge = document.getElementById('sentimentSignal');
    signalBadge.textContent = `${data.signal.action.toUpperCase()} (${data.signal.strength})`;
    signalBadge.className = `badge ${data.signal.action === 'buy' ? 'up' : data.signal.action === 'sell' ? 'down' : ''}`;
    
    // Sentiment Chart
    drawSentimentChart(data);
    
    // News Articles
    displayNewsArticles(data.articles);
    
    document.getElementById('sentimentResults').scrollIntoView({ behavior: 'smooth' });
}

function drawSentimentChart(data) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    if (window.sentimentChart) {
        window.sentimentChart.destroy();
    }
    
    window.sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [data.positive_count, data.negative_count, data.neutral_count],
                backgroundColor: ['#10b981', '#ef4444', '#6b7280']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function displayNewsArticles(articles) {
    const container = document.getElementById('newsArticles');
    container.innerHTML = '';
    
    articles.forEach(article => {
        const item = document.createElement('div');
        item.className = 'news-item';
        item.innerHTML = `
            <h4>${article.title}</h4>
            <p>${article.description || ''}</p>
            <div class="news-meta">
                <span>${article.source}</span>
                <span class="badge ${article.sentiment}">${article.sentiment}</span>
            </div>
        `;
        container.appendChild(item);
    });
}

// Portfolio Tab
document.getElementById('optimizeBtn').addEventListener('click', async () => {
    const symbolsInput = document.getElementById('portfolioSymbols').value.trim();
    const method = document.getElementById('optimizationMethod').value;
    const value = parseFloat(document.getElementById('portfolioValue').value);
    
    if (!symbolsInput) {
        alert('Please enter stock symbols');
        return;
    }
    
    const symbols = symbolsInput.split(',').map(s => s.trim().toUpperCase());
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/portfolio/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbols: symbols,
                optimization_method: method,
                portfolio_value: value
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayPortfolioResults(data);
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
});

function displayPortfolioResults(data) {
    document.getElementById('portfolioResults').style.display = 'block';
    
    // Metrics
    document.getElementById('portfolioReturn').textContent = `${data.metrics.expected_annual_return}%`;
    document.getElementById('portfolioVolatility').textContent = `${data.metrics.annual_volatility}%`;
    document.getElementById('portfolioSharpe').textContent = data.metrics.sharpe_ratio;
    document.getElementById('diversificationScore').textContent = `${data.metrics.diversification_score}/100`;
    
    // Allocation Chart
    drawAllocationChart(data.allocation.weights);
    
    // Allocation Table
    displayAllocationTable(data.allocation);
    
    // Risk Analysis
    displayRiskAnalysis(data.risk);
    
    // Recommendations
    displayRecommendations(data.recommendations);
    
    document.getElementById('portfolioResults').scrollIntoView({ behavior: 'smooth' });
}

function drawAllocationChart(weights) {
    const ctx = document.getElementById('allocationChart').getContext('2d');
    
    if (window.allocationChart) {
        window.allocationChart.destroy();
    }
    
    const symbols = Object.keys(weights);
    const percentages = Object.values(weights);
    
    window.allocationChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: symbols,
            datasets: [{
                data: percentages,
                backgroundColor: [
                    '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function displayAllocationTable(allocation) {
    const container = document.getElementById('allocationTable');
    
    let html = '<table><thead><tr><th>Symbol</th><th>Weight</th><th>Amount</th></tr></thead><tbody>';
    
    for (const [symbol, weight] of Object.entries(allocation.weights)) {
        html += `
            <tr>
                <td><strong>${symbol}</strong></td>
                <td>${weight}%</td>
                <td>$${allocation.dollars[symbol].toLocaleString()}</td>
            </tr>
        `;
    }
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function displayRiskAnalysis(risk) {
    const container = document.getElementById('riskAnalysis');
    container.innerHTML = `
        <div class="risk-item">
            <h4>Value at Risk (95%)</h4>
            <p>Maximum 1-day loss: $${risk.var_95.toLocaleString()}</p>
        </div>
        <div class="risk-item">
            <h4>Value at Risk (99%)</h4>
            <p>Maximum 1-day loss: $${risk.var_99.toLocaleString()}</p>
        </div>
        <div class="risk-item">
            <h4>Description</h4>
            <p>${risk.var_description}</p>
        </div>
    `;
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    container.innerHTML = '';
    
    recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        item.textContent = rec;
        container.appendChild(item);
    });
}

// Utility Functions
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function formatNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toLocaleString();
}
