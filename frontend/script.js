// Smart Financial Advisor - Enhanced Frontend JavaScript
// With 3D effects, animations, and improved visualizations

const API_BASE_URL = 'http://localhost:8000';

// ========================================
// Authentication & Search History
// ========================================
let currentUser = null;
let searchHistory = [];

// Check authentication on page load
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, { credentials: 'include' });
        if (response.ok) {
            currentUser = await response.json();
            updateUserUI();
            loadSearchHistory();
        } else {
            // Not logged in - redirect to login
            // window.location.href = '/login';
            console.log('Not logged in - guest mode');
        }
    } catch (error) {
        console.log('Auth check failed:', error);
    }
}

function updateUserUI() {
    // Update any user-related UI elements
    const userNameEl = document.querySelector('.user-name');
    const userAvatarEl = document.querySelector('.user-avatar');
    
    if (currentUser && userNameEl) {
        userNameEl.textContent = currentUser.name;
    }
    if (currentUser && userAvatarEl) {
        userAvatarEl.textContent = currentUser.name.charAt(0).toUpperCase();
    }
}

async function loadSearchHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/history`, { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            searchHistory = data.history || [];
            displaySearchHistory();
        }
    } catch (error) {
        console.log('Failed to load search history:', error);
    }
}

async function addToSearchHistory(symbol, type = 'stock') {
    try {
        await fetch(`${API_BASE_URL}/api/auth/history/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol: symbol, type: type }),
            credentials: 'include'
        });
        loadSearchHistory(); // Refresh history
    } catch (error) {
        console.log('Failed to add to history:', error);
    }
}

function displaySearchHistory() {
    const historyContainer = document.getElementById('searchHistory');
    if (!historyContainer || searchHistory.length === 0) return;
    
    historyContainer.innerHTML = '<h4>Recent Searches</h4>' + 
        searchHistory.slice(0, 5).map(item => 
            `<span class="history-tag" data-symbol="${item.symbol}" data-type="${item.type}">${item.symbol}</span>`
        ).join('');
    
    historyContainer.style.display = 'block';
    
    // Add click handlers
    historyContainer.querySelectorAll('.history-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            const input = document.getElementById('stockSymbol');
            if (input) input.value = tag.dataset.symbol;
        });
    });
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, { 
            method: 'POST',
            credentials: 'include' 
        });
        localStorage.removeItem('user');
        window.location.href = '/login';
    } catch (error) {
        console.log('Logout failed:', error);
    }
}

// Initialize auth check
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Add logout button handler if exists
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});

// ========================================
// Three.js 3D Background Scene
// ========================================
let scene, camera, renderer, particles;
let mouseX = 0, mouseY = 0;

function init3DScene() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Create particle system
    const particleCount = 1500;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);

    const colorPrimary = new THREE.Color(0x00f5ff);
    const colorSecondary = new THREE.Color(0xff00ff);

    for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 100;
        positions[i + 1] = (Math.random() - 0.5) * 100;
        positions[i + 2] = (Math.random() - 0.5) * 100;

        const color = Math.random() > 0.5 ? colorPrimary : colorSecondary;
        colors[i] = color.r;
        colors[i + 1] = color.g;
        colors[i + 2] = color.b;

        sizes[i / 3] = Math.random() * 2 + 0.5;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const material = new THREE.PointsMaterial({
        size: 1.5,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Add floating geometric shapes
    const shapes = [];
    const shapeGeometries = [
        new THREE.IcosahedronGeometry(2, 0),
        new THREE.OctahedronGeometry(2, 0),
        new THREE.TetrahedronGeometry(2, 0)
    ];

    for (let i = 0; i < 15; i++) {
        const geom = shapeGeometries[Math.floor(Math.random() * shapeGeometries.length)];
        const mat = new THREE.MeshBasicMaterial({
            color: Math.random() > 0.5 ? 0x00f5ff : 0xff00ff,
            wireframe: true,
            transparent: true,
            opacity: 0.3
        });
        const mesh = new THREE.Mesh(geom, mat);
        mesh.position.set(
            (Math.random() - 0.5) * 80,
            (Math.random() - 0.5) * 80,
            (Math.random() - 0.5) * 80
        );
        mesh.userData = {
            rotationSpeed: { x: Math.random() * 0.01, y: Math.random() * 0.01 },
            floatSpeed: Math.random() * 0.5 + 0.5,
            floatOffset: Math.random() * Math.PI * 2
        };
        shapes.push(mesh);
        scene.add(mesh);
    }

    camera.position.z = 50;

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);

        // Rotate particles
        if (particles) {
            particles.rotation.x += 0.0003;
            particles.rotation.y += 0.0005;
        }

        // Animate shapes
        shapes.forEach(shape => {
            shape.rotation.x += shape.userData.rotationSpeed.x;
            shape.rotation.y += shape.userData.rotationSpeed.y;
            shape.position.y += Math.sin(Date.now() * 0.001 * shape.userData.floatSpeed + shape.userData.floatOffset) * 0.02;
        });

        // Mouse interaction
        camera.position.x += (mouseX * 0.05 - camera.position.x) * 0.05;
        camera.position.y += (-mouseY * 0.05 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);

        renderer.render(scene, camera);
    }

    animate();

    // Handle resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// ========================================
// Custom Cursor
// ========================================
function initCustomCursor() {
    const cursorDot = document.querySelector('.cursor-dot');
    const cursorOutline = document.querySelector('.cursor-outline');
    
    if (!cursorDot || !cursorOutline) return;

    let cursorX = 0, cursorY = 0;
    let outlineX = 0, outlineY = 0;

    document.addEventListener('mousemove', (e) => {
        cursorX = e.clientX;
        cursorY = e.clientY;
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = (e.clientY / window.innerHeight) * 2 - 1;
    });

    function animateCursor() {
        cursorDot.style.left = cursorX + 'px';
        cursorDot.style.top = cursorY + 'px';

        outlineX += (cursorX - outlineX) * 0.15;
        outlineY += (cursorY - outlineY) * 0.15;
        cursorOutline.style.left = outlineX + 'px';
        cursorOutline.style.top = outlineY + 'px';

        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Hover effects
    const interactiveElements = document.querySelectorAll('button, a, input, .nav-btn, .pulse-tag, .tilt-card');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => cursorOutline.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursorOutline.classList.remove('hover'));
    });
}

// ========================================
// Vanilla Tilt Initialization
// ========================================
function initTiltEffects() {
    if (typeof VanillaTilt === 'undefined') return;

    const tiltElements = document.querySelectorAll('[data-tilt]');
    VanillaTilt.init(tiltElements, {
        max: 10,
        speed: 400,
        glare: true,
        'max-glare': 0.2,
        perspective: 1000
    });
}

// ========================================
// Floating Particles
// ========================================
function createFloatingParticles() {
    const container = document.querySelector('.particles-container');
    if (!container) return;

    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        container.appendChild(particle);
    }
}

// ========================================
// Live Ticker
// ========================================
function initLiveTicker() {
    const tickerContent = document.querySelector('.ticker-content');
    if (!tickerContent) return;

    const stocks = [
        { symbol: 'AAPL', price: 178.50, change: 2.3 },
        { symbol: 'GOOGL', price: 141.25, change: -0.8 },
        { symbol: 'TSLA', price: 245.70, change: 4.2 },
        { symbol: 'MSFT', price: 378.90, change: 1.1 },
        { symbol: 'AMZN', price: 178.20, change: -1.5 }
    ];

    let currentIndex = 0;
    
    function updateTicker() {
        const stock = stocks[currentIndex];
        const changeClass = stock.change >= 0 ? 'up' : 'down';
        const changeSymbol = stock.change >= 0 ? '+' : '';
        tickerContent.innerHTML = `
            <span>${stock.symbol}</span>
            <span style="color: var(--${stock.change >= 0 ? 'success' : 'danger'})">${changeSymbol}${stock.change}%</span>
        `;
        currentIndex = (currentIndex + 1) % stocks.length;
    }

    updateTicker();
    setInterval(updateTicker, 3000);
}

// ========================================
// GSAP Animations
// ========================================
function initGSAPAnimations() {
    if (typeof gsap === 'undefined') return;

    // Header animation
    gsap.from('.header', {
        y: -100,
        opacity: 0,
        duration: 1,
        ease: 'power3.out'
    });

    // Logo animation
    gsap.from('.logo', {
        x: -50,
        opacity: 0,
        duration: 1,
        delay: 0.3,
        ease: 'power3.out'
    });

    // Navigation animation
    gsap.from('.nav-btn', {
        y: -30,
        opacity: 0,
        duration: 0.5,
        stagger: 0.1,
        delay: 0.5,
        ease: 'power3.out'
    });

    // Search section animation
    gsap.from('.search-section', {
        y: 50,
        opacity: 0,
        duration: 1,
        delay: 0.8,
        ease: 'power3.out'
    });

    // ScrollTrigger for results
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        gsap.utils.toArray('.glass-card').forEach(card => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    toggleActions: 'play none none reverse'
                },
                y: 50,
                opacity: 0,
                duration: 0.8,
                ease: 'power3.out'
            });
        });
    }
}

// ========================================
// Initialize All 3D Effects
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    init3DScene();
    initCustomCursor();
    initTiltEffects();
    createFloatingParticles();
    initLiveTicker();
    initGSAPAnimations();
});

// ========================================
// Tab Navigation
// ========================================
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

// ========================================
// Popular Stock Tags
// ========================================
document.querySelectorAll('.stock-tag').forEach(tag => {
    tag.addEventListener('click', () => {
        document.getElementById('stockSymbol').value = tag.dataset.symbol;
    });
});

// ========================================
// Portfolio Presets
// ========================================
document.querySelectorAll('.portfolio-preset').forEach(preset => {
    preset.addEventListener('click', () => {
        document.getElementById('portfolioSymbols').value = preset.dataset.symbols;
    });
});

// ========================================
// Prediction Tab
// ========================================
document.getElementById('predictBtn').addEventListener('click', async () => {
    const symbol = document.getElementById('stockSymbol').value.toUpperCase().trim();
    const days = parseInt(document.getElementById('predictionDays').value);
    
    if (!symbol) {
        showToast('Please enter a stock symbol', 'error');
        return;
    }
    
    showLoading(true);
    
    // Add to search history
    addToSearchHistory(symbol, 'stock');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/predict/${symbol}?days=${days}`);
        const data = await response.json();
        
        if (response.ok) {
            displayPredictionResults(data);
        } else {
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
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
    document.getElementById('stockInitial').textContent = data.symbol.charAt(0);
    
    // Animate current price
    animateNumber('currentPrice', data.current_price, '$', 2);
    
    // Today's change indicator
    const changeIndicator = document.getElementById('priceChangeIndicator');
    const isUp = data.summary.direction === 'up';
    changeIndicator.className = `price-change ${isUp ? 'up' : 'down'}`;
    document.getElementById('todayChange').textContent = `${isUp ? '+' : ''}${data.summary.price_change_percent}%`;
    
    // Stock info grid
    animateNumber('marketCap', data.stock_info.marketCap, '', 0, true);
    animateNumber('peRatio', data.stock_info.pe_ratio, '', 2);
    animateNumber('volume', data.stock_info.volume, '', 0, true);
    animateNumber('beta', data.stock_info.beta, '', 2);
    
    // Prediction Summary
    animateNumber('predictedPrice', parseFloat(data.summary.predicted_price), '$', 2);
    document.getElementById('priceChange').textContent = 
        `$${data.summary.price_change} (${data.summary.price_change_percent}%)`;
    
    // Direction Badge
    const directionBadge = document.getElementById('direction');
    directionBadge.className = `badge direction-badge ${data.summary.direction}`;
    directionBadge.querySelector('span').textContent = data.summary.direction.toUpperCase();
    
    // Recommendation Badge
    const recBadge = document.getElementById('recommendation');
    recBadge.textContent = data.summary.recommendation;
    recBadge.className = `badge recommendation-badge ${data.summary.direction}`;
    
    // Confidence Bar
    const confidenceValue = data.model_metrics ? Math.min(95, 100 - data.model_metrics.test_rmse) : 95;
    document.getElementById('confidenceFill').style.width = `${confidenceValue}%`;
    document.getElementById('confidenceText').textContent = `${confidenceValue.toFixed(0)}% Confidence`;
    
    // Model Metrics
    if (data.model_metrics) {
        document.getElementById('metricsCard').style.display = 'block';
        animateNumber('testRmse', data.model_metrics.test_rmse, '', 2);
        animateNumber('testMae', data.model_metrics.test_mae, '', 2);
        animateNumber('r2Score', data.model_metrics.test_r2, '', 4);
        document.getElementById('confidence').textContent = `${confidenceValue.toFixed(0)}%`;
    }
    
    // Draw Enhanced Chart
    drawPredictionChart(data);
    
    // Update Technical Indicators
    updateTechnicalIndicators(data);
    
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
    
    // Create gradient for historical prices - Cyberpunk cyan
    const historicalGradient = ctx.createLinearGradient(0, 0, 0, 400);
    historicalGradient.addColorStop(0, 'rgba(0, 245, 255, 0.4)');
    historicalGradient.addColorStop(1, 'rgba(0, 245, 255, 0)');
    
    // Create gradient for predictions - Cyberpunk magenta
    const predictionGradient = ctx.createLinearGradient(0, 0, 0, 400);
    predictionGradient.addColorStop(0, 'rgba(255, 0, 255, 0.4)');
    predictionGradient.addColorStop(1, 'rgba(255, 0, 255, 0)');
    
    window.predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: [
                {
                    label: 'Historical Price',
                    data: allPrices,
                    borderColor: '#00f5ff',
                    backgroundColor: historicalGradient,
                    borderWidth: 3,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#00f5ff',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Predicted Price',
                    data: predictions,
                    borderColor: '#ff00ff',
                    backgroundColor: predictionGradient,
                    borderWidth: 3,
                    borderDash: [8, 4],
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#ff00ff',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Upper Bound',
                    data: upperBound,
                    borderColor: 'rgba(255, 255, 0, 0.5)',
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    borderDash: [4, 4],
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: 'Lower Bound',
                    data: lowerBound,
                    borderColor: 'rgba(255, 255, 0, 0.5)',
                    backgroundColor: 'rgba(255, 255, 0, 0.1)',
                    borderWidth: 1,
                    borderDash: [4, 4],
                    pointRadius: 0,
                    fill: '-1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 20, 0.95)',
                    titleColor: '#00f5ff',
                    bodyColor: '#8892b0',
                    borderColor: 'rgba(0, 245, 255, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            if (context.raw === null) return null;
                            return `${context.dataset.label}: $${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 245, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8892b0',
                        maxTicksLimit: 10,
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 245, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8892b0',
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        },
                        font: {
                            size: 11
                        }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function updateTechnicalIndicators(data) {
    // Generate mock technical indicators based on prediction data
    const prices = data.historical_data.prices;
    const currentPrice = data.current_price;
    
    // RSI Calculation (simplified)
    const rsi = calculateRSI(prices);
    document.getElementById('rsiValue').textContent = rsi.toFixed(1);
    document.getElementById('rsiFill').style.width = `${rsi}%`;
    
    const rsiSignal = document.getElementById('rsiSignal');
    if (rsi < 30) {
        rsiSignal.textContent = 'Oversold';
        rsiSignal.className = 'indicator-signal bullish';
    } else if (rsi > 70) {
        rsiSignal.textContent = 'Overbought';
        rsiSignal.className = 'indicator-signal bearish';
    } else {
        rsiSignal.textContent = 'Neutral';
        rsiSignal.className = 'indicator-signal';
    }
    
    // MACD Visual
    const macdContainer = document.getElementById('macdBars');
    macdContainer.innerHTML = '';
    const macdData = generateMACDData(prices);
    macdData.forEach(value => {
        const bar = document.createElement('div');
        bar.className = `macd-bar ${value > 0 ? 'positive' : 'negative'}`;
        bar.style.height = `${Math.min(Math.abs(value) * 10, 100)}%`;
        macdContainer.appendChild(bar);
    });
    
    document.getElementById('macdValue').textContent = macdData[macdData.length - 1].toFixed(2);
    const macdSignal = document.getElementById('macdSignal');
    macdSignal.textContent = macdData[macdData.length - 1] > 0 ? 'Bullish' : 'Bearish';
    macdSignal.className = `indicator-signal ${macdData[macdData.length - 1] > 0 ? 'bullish' : 'bearish'}`;
    
    // Moving Averages
    const sma20 = calculateSMA(prices, 20);
    const sma50 = calculateSMA(prices, 50);
    const sma200 = calculateSMA(prices, Math.min(200, prices.length));
    
    document.getElementById('sma20').textContent = `$${sma20.toFixed(2)}`;
    document.getElementById('sma50').textContent = `$${sma50.toFixed(2)}`;
    document.getElementById('sma200').textContent = `$${sma200.toFixed(2)}`;
    
    const maSignal = document.getElementById('maSignal');
    if (currentPrice > sma20 && sma20 > sma50) {
        maSignal.textContent = 'Bullish';
        maSignal.className = 'indicator-signal bullish';
        document.getElementById('maValue').textContent = 'Golden Cross';
    } else if (currentPrice < sma20 && sma20 < sma50) {
        maSignal.textContent = 'Bearish';
        maSignal.className = 'indicator-signal bearish';
        document.getElementById('maValue').textContent = 'Death Cross';
    } else {
        maSignal.textContent = 'Neutral';
        maSignal.className = 'indicator-signal';
        document.getElementById('maValue').textContent = 'Consolidating';
    }
    
    // Bollinger Bands
    const bbData = calculateBollingerBands(prices);
    const bbPosition = document.getElementById('bbPosition');
    const pricePosition = (currentPrice - bbData.lower) / (bbData.upper - bbData.lower);
    bbPosition.style.left = `${Math.max(5, Math.min(95, pricePosition * 100))}%`;
    
    document.getElementById('bbValue').textContent = `$${bbData.middle.toFixed(2)}`;
    const bbSignal = document.getElementById('bbSignal');
    if (currentPrice > bbData.upper) {
        bbSignal.textContent = 'Overbought';
        bbSignal.className = 'indicator-signal bearish';
    } else if (currentPrice < bbData.lower) {
        bbSignal.textContent = 'Oversold';
        bbSignal.className = 'indicator-signal bullish';
    } else {
        bbSignal.textContent = 'Normal';
        bbSignal.className = 'indicator-signal';
    }
}

// ========================================
// Sentiment Tab
// ========================================
document.getElementById('analyzeSentimentBtn').addEventListener('click', async () => {
    const symbol = document.getElementById('sentimentSymbol').value.toUpperCase().trim();
    
    if (!symbol) {
        showToast('Please enter a stock symbol', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/sentiment/${symbol}`);
        const data = await response.json();
        
        if (response.ok) {
            displaySentimentResults(data);
        } else {
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
});

function displaySentimentResults(data) {
    document.getElementById('sentimentResults').style.display = 'block';
    
    // Sentiment Score Ring
    const ringProgress = document.getElementById('sentimentProgress');
    const scoreValue = ((data.score + 1) / 2) * 100; // Convert -1 to 1 range to 0-100
    const strokeOffset = 283 - (scoreValue / 100) * 283;
    
    ringProgress.style.strokeDashoffset = strokeOffset;
    ringProgress.classList.remove('positive', 'negative');
    ringProgress.classList.add(data.sentiment);
    
    // Animate score
    animateNumber('sentimentScore', data.score, '', 2);
    document.getElementById('sentimentLabel').textContent = data.sentiment.toUpperCase();
    
    // Emoji
    const emoji = document.getElementById('sentimentEmoji');
    emoji.textContent = data.sentiment === 'positive' ? '😊' : data.sentiment === 'negative' ? '😞' : '😐';
    
    // Confidence Progress
    const confidencePercent = data.confidence * 100;
    document.getElementById('sentimentConfidence').style.width = `${confidencePercent}%`;
    document.getElementById('confidenceValue').textContent = `${confidencePercent.toFixed(0)}%`;
    
    // Other details
    animateNumber('articlesAnalyzed', data.articles_analyzed, '', 0);
    document.getElementById('sentimentImpact').textContent = data.impact;
    
    // Signal Badge
    const signalBadge = document.getElementById('sentimentSignal');
    signalBadge.textContent = `${data.signal.action.toUpperCase()} (${data.signal.strength})`;
    signalBadge.className = `badge signal-badge ${data.signal.action === 'buy' ? 'up' : data.signal.action === 'sell' ? 'down' : ''}`;
    
    // Update sentiment stats
    const total = data.positive_count + data.negative_count + data.neutral_count;
    document.getElementById('positiveCount').textContent = data.positive_count;
    document.getElementById('negativeCount').textContent = data.negative_count;
    document.getElementById('neutralCount').textContent = data.neutral_count;
    
    document.getElementById('positiveFill').style.width = `${(data.positive_count / total) * 100}%`;
    document.getElementById('negativeFill').style.width = `${(data.negative_count / total) * 100}%`;
    document.getElementById('neutralFill').style.width = `${(data.neutral_count / total) * 100}%`;
    
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
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(100, 116, 139, 0.8)'
                ],
                borderColor: [
                    '#10b981',
                    '#ef4444',
                    '#64748b'
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

function displayNewsArticles(articles) {
    const container = document.getElementById('newsArticles');
    container.innerHTML = '';
    
    articles.forEach((article, index) => {
        const item = document.createElement('div');
        item.className = 'news-item animate-in';
        item.style.animationDelay = `${index * 0.1}s`;
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

// ========================================
// Portfolio Tab
// ========================================
document.getElementById('optimizeBtn').addEventListener('click', async () => {
    const symbolsInput = document.getElementById('portfolioSymbols').value.trim();
    const method = document.getElementById('optimizationMethod').value;
    const value = parseFloat(document.getElementById('portfolioValue').value);
    
    if (!symbolsInput) {
        showToast('Please enter stock symbols', 'error');
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
            showToast(`Error: ${data.detail}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
});

function displayPortfolioResults(data) {
    document.getElementById('portfolioResults').style.display = 'block';
    
    // Animate metrics with ring progress
    const returnValue = parseFloat(data.metrics.expected_annual_return);
    const volatilityValue = parseFloat(data.metrics.annual_volatility);
    
    // Return Ring
    const returnRing = document.getElementById('returnRing');
    const returnOffset = 283 - (Math.min(returnValue, 100) / 100) * 283;
    returnRing.style.strokeDashoffset = returnOffset;
    document.querySelector('#returnRing + .ring-value').textContent = `${returnValue}%`;
    
    // Volatility Ring
    const volatilityRing = document.getElementById('volatilityRing');
    const volatilityOffset = 283 - (Math.min(volatilityValue, 100) / 100) * 283;
    volatilityRing.style.strokeDashoffset = volatilityOffset;
    document.querySelector('#volatilityRing + .ring-value').textContent = `${volatilityValue}%`;
    
    // Other metrics
    animateNumber('portfolioSharpe', parseFloat(data.metrics.sharpe_ratio), '', 2);
    document.getElementById('diversificationScore').textContent = `${data.metrics.diversification_score}/100`;
    
    // Allocation Chart and Legend
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
    
    const colors = [
        '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
        '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
    ];
    
    window.allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: symbols,
            datasets: [{
                data: percentages,
                backgroundColor: colors.slice(0, symbols.length).map(c => c + 'cc'),
                borderColor: colors.slice(0, symbols.length),
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '60%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1200,
                easing: 'easeOutQuart'
            }
        }
    });
    
    // Create legend
    const legendContainer = document.getElementById('allocationLegend');
    legendContainer.innerHTML = '';
    
    symbols.forEach((symbol, index) => {
        const item = document.createElement('div');
        item.className = 'allocation-legend-item';
        item.innerHTML = `
            <span class="legend-dot" style="background-color: ${colors[index]}"></span>
            <span class="legend-symbol">${symbol}</span>
            <span class="legend-percent">${percentages[index]}%</span>
        `;
        legendContainer.appendChild(item);
    });
}

function displayAllocationTable(allocation) {
    const container = document.getElementById('allocationTable');
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Weight</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
    `;
    
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
            <p>Maximum expected 1-day loss with 95% confidence: <strong>$${risk.var_95.toLocaleString()}</strong></p>
        </div>
        <div class="risk-item">
            <h4>Value at Risk (99%)</h4>
            <p>Maximum expected 1-day loss with 99% confidence: <strong>$${risk.var_99.toLocaleString()}</strong></p>
        </div>
        <div class="risk-item">
            <h4>Risk Description</h4>
            <p>${risk.var_description}</p>
        </div>
    `;
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    container.innerHTML = '';
    
    recommendations.forEach((rec, index) => {
        const item = document.createElement('div');
        item.className = 'recommendation-item animate-in';
        item.style.animationDelay = `${index * 0.1}s`;
        item.textContent = rec;
        container.appendChild(item);
    });
}

// ========================================
// Utility Functions
// ========================================
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#6366f1'};
        color: white;
        border-radius: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function animateNumber(elementId, targetValue, prefix = '', decimals = 0, isLargeNumber = false) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const start = 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function formatValue(value) {
        if (isLargeNumber) {
            return prefix + formatLargeNumber(value);
        }
        return prefix + value.toFixed(decimals);
    }
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 4); // easeOutQuart
        
        const currentValue = start + (targetValue - start) * easeProgress;
        element.textContent = formatValue(currentValue);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = formatValue(targetValue);
        }
    }
    
    requestAnimationFrame(update);
}

function formatLargeNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toLocaleString();
}

// Technical Indicator Calculations
function calculateRSI(prices, period = 14) {
    if (prices.length < period + 1) return 50;
    
    let gains = 0;
    let losses = 0;
    
    for (let i = prices.length - period; i < prices.length; i++) {
        const change = prices[i] - prices[i - 1];
        if (change > 0) gains += change;
        else losses -= change;
    }
    
    const avgGain = gains / period;
    const avgLoss = losses / period;
    
    if (avgLoss === 0) return 100;
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
}

function calculateSMA(prices, period) {
    if (prices.length < period) return prices[prices.length - 1];
    const slice = prices.slice(-period);
    return slice.reduce((a, b) => a + b, 0) / period;
}

function generateMACDData(prices) {
    const result = [];
    for (let i = 0; i < 20; i++) {
        const idx = Math.max(0, prices.length - 20 + i);
        const shortEMA = calculateEMA(prices.slice(0, idx + 1), 12);
        const longEMA = calculateEMA(prices.slice(0, idx + 1), 26);
        result.push(shortEMA - longEMA);
    }
    return result;
}

function calculateEMA(prices, period) {
    if (prices.length === 0) return 0;
    if (prices.length < period) return prices[prices.length - 1];
    
    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;
    
    for (let i = period; i < prices.length; i++) {
        ema = (prices[i] - ema) * multiplier + ema;
    }
    return ema;
}

function calculateBollingerBands(prices, period = 20) {
    const sma = calculateSMA(prices, period);
    const slice = prices.slice(-period);
    const squaredDiffs = slice.map(p => Math.pow(p - sma, 2));
    const stdDev = Math.sqrt(squaredDiffs.reduce((a, b) => a + b, 0) / period);
    
    return {
        upper: sma + (stdDev * 2),
        middle: sma,
        lower: sma - (stdDev * 2)
    };
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ========================================
// Initialize
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Smart Financial Advisor loaded');
    
    // Add GSAP animations if available
    if (typeof gsap !== 'undefined') {
        gsap.from('.header', { 
            y: -100, 
            opacity: 0, 
            duration: 1, 
            ease: 'power3.out' 
        });
        
        gsap.from('.search-section', { 
            y: 50, 
            opacity: 0, 
            duration: 0.8, 
            delay: 0.3,
            ease: 'power3.out' 
        });
    }
});
