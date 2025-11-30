"""
Portfolio Optimization using Modern Portfolio Theory
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Portfolio optimization based on Modern Portfolio Theory"""
    
    def __init__(self, risk_free_rate: float = 0.04):
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily returns from price data"""
        return prices.pct_change().dropna()
    
    def calculate_portfolio_metrics(self, weights: np.ndarray, returns: pd.DataFrame) -> Tuple[float, float]:
        """Calculate portfolio return and risk"""
        # Annualized return
        portfolio_return = np.sum(returns.mean() * weights) * 252
        
        # Annualized volatility
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        return portfolio_return, portfolio_std
    
    def calculate_sharpe_ratio(self, weights: np.ndarray, returns: pd.DataFrame) -> float:
        """Calculate Sharpe ratio"""
        portfolio_return, portfolio_std = self.calculate_portfolio_metrics(weights, returns)
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        return sharpe_ratio
    
    def negative_sharpe(self, weights: np.ndarray, returns: pd.DataFrame) -> float:
        """Negative Sharpe ratio for minimization"""
        return -self.calculate_sharpe_ratio(weights, returns)
    
    def optimize_sharpe(self, returns: pd.DataFrame) -> Dict:
        """Optimize portfolio for maximum Sharpe ratio"""
        n_assets = len(returns.columns)
        
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            self.negative_sharpe,
            initial_weights,
            args=(returns,),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            portfolio_return, portfolio_std = self.calculate_portfolio_metrics(optimal_weights, returns)
            sharpe_ratio = self.calculate_sharpe_ratio(optimal_weights, returns)
            
            return {
                'weights': dict(zip(returns.columns, optimal_weights)),
                'expected_return': round(portfolio_return * 100, 2),
                'volatility': round(portfolio_std * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'success': True
            }
        else:
            return {'success': False, 'message': 'Optimization failed'}
    
    def optimize_min_volatility(self, returns: pd.DataFrame) -> Dict:
        """Optimize portfolio for minimum volatility"""
        n_assets = len(returns.columns)
        
        def portfolio_volatility(weights):
            return self.calculate_portfolio_metrics(weights, returns)[1]
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            portfolio_return, portfolio_std = self.calculate_portfolio_metrics(optimal_weights, returns)
            sharpe_ratio = self.calculate_sharpe_ratio(optimal_weights, returns)
            
            return {
                'weights': dict(zip(returns.columns, optimal_weights)),
                'expected_return': round(portfolio_return * 100, 2),
                'volatility': round(portfolio_std * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'success': True
            }
        else:
            return {'success': False, 'message': 'Optimization failed'}
    
    def efficient_frontier(self, returns: pd.DataFrame, n_points: int = 50) -> Dict:
        """Calculate efficient frontier"""
        n_assets = len(returns.columns)
        
        # Calculate min and max returns
        min_ret = returns.mean().min() * 252
        max_ret = returns.mean().max() * 252
        target_returns = np.linspace(min_ret, max_ret, n_points)
        
        frontier_volatility = []
        frontier_returns = []
        frontier_weights = []
        
        for target in target_returns:
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: self.calculate_portfolio_metrics(x, returns)[0] - target}
            ]
            
            bounds = tuple((0, 1) for _ in range(n_assets))
            initial_weights = np.array([1/n_assets] * n_assets)
            
            result = minimize(
                lambda w: self.calculate_portfolio_metrics(w, returns)[1],
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                weights = result.x
                ret, vol = self.calculate_portfolio_metrics(weights, returns)
                frontier_returns.append(ret * 100)
                frontier_volatility.append(vol * 100)
                frontier_weights.append(dict(zip(returns.columns, weights)))
        
        return {
            'returns': frontier_returns,
            'volatility': frontier_volatility,
            'weights': frontier_weights
        }
    
    def calculate_var(self, returns: pd.DataFrame, weights: np.ndarray, 
                     confidence: float = 0.95, portfolio_value: float = 100000) -> float:
        """Calculate Value at Risk (VaR)"""
        portfolio_returns = (returns * weights).sum(axis=1)
        var = np.percentile(portfolio_returns, (1 - confidence) * 100) * portfolio_value
        return abs(var)
    
    def diversification_score(self, weights: Dict) -> float:
        """Calculate diversification score (0-100)"""
        weight_values = list(weights.values())
        # Perfect diversification = equal weights
        ideal_weight = 1.0 / len(weight_values)
        deviations = [abs(w - ideal_weight) for w in weight_values]
        score = 100 * (1 - (sum(deviations) / 2))  # Normalize to 0-100
        return round(score, 2)


if __name__ == "__main__":
    # Test
    print("Portfolio Optimizer initialized")
