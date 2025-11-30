"""
API Routes for Portfolio Management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.portfolio_optimizer import PortfolioOptimizer
from data.stock_data import StockDataFetcher

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])

# Initialize services
optimizer = PortfolioOptimizer()
fetcher = StockDataFetcher()


class PortfolioRequest(BaseModel):
    symbols: List[str]
    optimization_method: str = "sharpe"  # sharpe, min_volatility
    portfolio_value: float = 100000


class RiskAnalysisRequest(BaseModel):
    symbols: List[str]
    weights: Dict[str, float]
    portfolio_value: float = 100000


@router.post("/optimize")
async def optimize_portfolio(request: PortfolioRequest):
    """
    Optimize portfolio allocation
    
    - **symbols**: List of stock symbols
    - **optimization_method**: 'sharpe' or 'min_volatility'
    - **portfolio_value**: Total portfolio value
    """
    try:
        # Fetch data for all symbols
        stock_data = fetcher.get_multiple_stocks(request.symbols)
        
        # Create price dataframe
        prices = pd.DataFrame()
        for symbol, df in stock_data.items():
            if df is not None:
                prices[symbol] = df['Close']
        
        if prices.empty:
            raise ValueError("No valid stock data found")
        
        # Calculate returns
        returns = optimizer.calculate_returns(prices)
        
        # Optimize based on method
        if request.optimization_method == "sharpe":
            result = optimizer.optimize_sharpe(returns)
        elif request.optimization_method == "min_volatility":
            result = optimizer.optimize_min_volatility(returns)
        else:
            raise ValueError(f"Unknown optimization method: {request.optimization_method}")
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('message', 'Optimization failed'))
        
        # Calculate allocation in dollars
        allocation_dollars = {
            symbol: round(weight * request.portfolio_value, 2)
            for symbol, weight in result['weights'].items()
        }
        
        # Calculate diversification score
        diversification = optimizer.diversification_score(result['weights'])
        
        # Calculate VaR
        weights_array = [result['weights'][symbol] for symbol in prices.columns]
        var_95 = optimizer.calculate_var(returns, weights_array, 0.95, request.portfolio_value)
        var_99 = optimizer.calculate_var(returns, weights_array, 0.99, request.portfolio_value)
        
        return {
            'optimization_method': request.optimization_method,
            'portfolio_value': request.portfolio_value,
            'allocation': {
                'weights': {k: round(v * 100, 2) for k, v in result['weights'].items()},
                'dollars': allocation_dollars
            },
            'metrics': {
                'expected_annual_return': result['expected_return'],
                'annual_volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio'],
                'diversification_score': diversification
            },
            'risk': {
                'var_95': round(var_95, 2),
                'var_99': round(var_99, 2),
                'var_description': f"95% confident losses won't exceed ${var_95:,.2f} in a day"
            },
            'recommendations': generate_recommendations(result, diversification)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-analysis")
async def analyze_risk(request: RiskAnalysisRequest):
    """Analyze risk for a given portfolio"""
    try:
        # Fetch data
        stock_data = fetcher.get_multiple_stocks(request.symbols)
        
        prices = pd.DataFrame()
        for symbol, df in stock_data.items():
            if df is not None:
                prices[symbol] = df['Close']
        
        returns = optimizer.calculate_returns(prices)
        
        # Convert weights to array
        weights_array = [request.weights.get(symbol, 0) for symbol in prices.columns]
        
        # Calculate metrics
        portfolio_return, portfolio_std = optimizer.calculate_portfolio_metrics(weights_array, returns)
        sharpe = optimizer.calculate_sharpe_ratio(weights_array, returns)
        var_95 = optimizer.calculate_var(returns, weights_array, 0.95, request.portfolio_value)
        var_99 = optimizer.calculate_var(returns, weights_array, 0.99, request.portfolio_value)
        
        # Diversification
        diversification = optimizer.diversification_score(request.weights)
        
        # Risk level
        risk_level = get_risk_level(portfolio_std * 100)
        
        return {
            'portfolio_value': request.portfolio_value,
            'weights': {k: round(v * 100, 2) for k, v in request.weights.items()},
            'metrics': {
                'expected_annual_return': round(portfolio_return * 100, 2),
                'annual_volatility': round(portfolio_std * 100, 2),
                'sharpe_ratio': round(sharpe, 3),
                'diversification_score': diversification
            },
            'risk_assessment': {
                'risk_level': risk_level,
                'var_95': round(var_95, 2),
                'var_99': round(var_99, 2),
                'max_drawdown_estimate': round(portfolio_std * 2 * request.portfolio_value, 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/efficient-frontier")
async def get_efficient_frontier(symbols: List[str]):
    """Calculate efficient frontier for given stocks"""
    try:
        stock_data = fetcher.get_multiple_stocks(symbols)
        
        prices = pd.DataFrame()
        for symbol, df in stock_data.items():
            if df is not None:
                prices[symbol] = df['Close']
        
        returns = optimizer.calculate_returns(prices)
        frontier = optimizer.efficient_frontier(returns, n_points=50)
        
        return {
            'symbols': symbols,
            'frontier': frontier
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_recommendations(optimization_result: dict, diversification_score: float) -> List[str]:
    """Generate portfolio recommendations"""
    recommendations = []
    
    if optimization_result['sharpe_ratio'] > 1.5:
        recommendations.append("✓ Excellent risk-adjusted returns")
    elif optimization_result['sharpe_ratio'] > 1.0:
        recommendations.append("✓ Good risk-adjusted returns")
    else:
        recommendations.append("⚠ Consider adjusting allocation for better returns")
    
    if diversification_score > 80:
        recommendations.append("✓ Well-diversified portfolio")
    elif diversification_score > 60:
        recommendations.append("⚠ Moderate diversification - consider adding more stocks")
    else:
        recommendations.append("⚠ Poor diversification - highly concentrated portfolio")
    
    if optimization_result['volatility'] < 15:
        recommendations.append("✓ Low volatility - suitable for conservative investors")
    elif optimization_result['volatility'] < 25:
        recommendations.append("✓ Moderate volatility - balanced risk")
    else:
        recommendations.append("⚠ High volatility - only for aggressive investors")
    
    return recommendations


def get_risk_level(volatility: float) -> dict:
    """Determine risk level from volatility"""
    if volatility < 10:
        return {'level': 'Low', 'color': 'green', 'description': 'Conservative portfolio'}
    elif volatility < 20:
        return {'level': 'Moderate', 'color': 'yellow', 'description': 'Balanced portfolio'}
    else:
        return {'level': 'High', 'color': 'red', 'description': 'Aggressive portfolio'}
