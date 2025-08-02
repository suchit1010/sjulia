#!/usr/bin/env python3
"""
Advanced Strategy Backtesting Engine with Agent Swarm
Professional backtesting for DeFi portfolio optimization strategies

Features:
- Historical data backtesting
- Multi-strategy comparison
- Risk-adjusted returns analysis
- Agent swarm coordination for strategy optimization
- Monte Carlo simulations
- Performance attribution analysis
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Results from strategy backtesting"""
    strategy_name: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    calmar_ratio: float
    sortino_ratio: float
    trades_count: int
    avg_trade_duration: float  # days
    best_trade: float
    worst_trade: float
    final_portfolio_value: float
    daily_returns: List[float]
    portfolio_values: List[float]
    trade_history: List[Dict[str, Any]]

@dataclass
class TradingStrategy:
    """Trading strategy definition"""
    name: str
    description: str
    strategy_type: str  # 'arbitrage', 'staking', 'market_making', 'rebalancing'
    parameters: Dict[str, Any]
    risk_level: str  # 'low', 'medium', 'high'
    expected_apy: float
    capital_allocation: float  # percentage of portfolio

@dataclass
class MarketData:
    """Historical market data"""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    volatility: float

class HistoricalDataProvider:
    """Provides historical market data for backtesting"""
    
    def __init__(self):
        self.session = None
        self.data_cache = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_historical_prices(self, symbol: str, days: int = 365) -> List[MarketData]:
        """Get historical price data"""
        try:
            # Use CoinGecko API for historical data
            token_ids = {
                'SOL': 'solana',
                'ETH': 'ethereum',
                'BTC': 'bitcoin',
                'USDC': 'usd-coin',
                'USDT': 'tether'
            }
            
            if symbol not in token_ids:
                logger.warning(f"Unknown symbol: {symbol}")
                return []
            
            token_id = token_ids[symbol]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart/range"
            params = {
                'vs_currency': 'usd',
                'from': int(start_date.timestamp()),
                'to': int(end_date.timestamp())
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    market_data = []
                    
                    prices = data.get('prices', [])
                    volumes = data.get('total_volumes', [])
                    
                    for i, (timestamp_ms, price) in enumerate(prices):
                        timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                        volume = volumes[i][1] if i < len(volumes) else 0
                        
                        # Calculate volatility (simplified)
                        volatility = self._calculate_volatility(prices, i)
                        
                        market_data.append(MarketData(
                            timestamp=timestamp,
                            symbol=symbol,
                            price=price,
                            volume=volume,
                            volatility=volatility
                        ))
                    
                    logger.info(f"Retrieved {len(market_data)} data points for {symbol}")
                    return market_data
                else:
                    logger.error(f"Failed to get data for {symbol}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
    
    def _calculate_volatility(self, prices: List[Tuple[int, float]], index: int, window: int = 20) -> float:
        """Calculate rolling volatility"""
        try:
            if index < window:
                return 0.0
            
            recent_prices = [prices[i][1] for i in range(max(0, index - window), index)]
            if len(recent_prices) < 2:
                return 0.0
            
            returns = [np.log(recent_prices[i] / recent_prices[i-1]) for i in range(1, len(recent_prices))]
            return np.std(returns) * np.sqrt(365)  # Annualized volatility
            
        except Exception:
            return 0.0

class StrategyBacktester:
    """Advanced strategy backtesting engine"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.data_provider = None
        self.strategies = []
        
    async def __aenter__(self):
        self.data_provider = await HistoricalDataProvider().__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.data_provider:
            await self.data_provider.__aexit__(exc_type, exc_val, exc_tb)
    
    def add_strategy(self, strategy: TradingStrategy):
        """Add a strategy to backtest"""
        self.strategies.append(strategy)
    
    async def run_backtest(self, strategy: TradingStrategy, days: int = 365) -> BacktestResult:
        """Run backtest for a single strategy"""
        logger.info(f"Starting backtest for strategy: {strategy.name}")
        
        try:
            # Get historical data for relevant assets
            historical_data = await self._get_strategy_data(strategy, days)
            
            if not historical_data:
                logger.error(f"No historical data available for {strategy.name}")
                return self._create_empty_result(strategy)
            
            # Run strategy simulation
            result = await self._simulate_strategy(strategy, historical_data)
            
            logger.info(f"Backtest completed for {strategy.name}: {result.annualized_return:.2%} return")
            return result
            
        except Exception as e:
            logger.error(f"Error in backtest for {strategy.name}: {e}")
            return self._create_empty_result(strategy)
    
    async def _get_strategy_data(self, strategy: TradingStrategy, days: int) -> Dict[str, List[MarketData]]:
        """Get historical data for strategy"""
        data = {}
        
        # Define assets needed based on strategy type
        if strategy.strategy_type == 'arbitrage':
            symbols = ['SOL', 'ETH', 'BTC']
        elif strategy.strategy_type == 'staking':
            symbols = ['SOL', 'ETH']
        elif strategy.strategy_type == 'market_making':
            symbols = ['SOL', 'USDC']
        else:  # rebalancing
            symbols = ['SOL', 'ETH', 'BTC', 'USDC']
        
        # Get data for each symbol
        for symbol in symbols:
            symbol_data = await self.data_provider.get_historical_prices(symbol, days)
            if symbol_data:
                data[symbol] = symbol_data
        
        return data
    
    async def _simulate_strategy(self, strategy: TradingStrategy, historical_data: Dict[str, List[MarketData]]) -> BacktestResult:
        """Simulate strategy execution"""
        try:
            capital = self.initial_capital * (strategy.capital_allocation / 100)
            portfolio_values = [capital]
            daily_returns = []
            trade_history = []
            
            # Get the shortest data series to align all data
            min_length = min(len(data) for data in historical_data.values())
            
            # Simulate strategy based on type
            if strategy.strategy_type == 'staking':
                result = self._simulate_staking_strategy(strategy, historical_data, capital, min_length)
            elif strategy.strategy_type == 'arbitrage':
                result = self._simulate_arbitrage_strategy(strategy, historical_data, capital, min_length)
            elif strategy.strategy_type == 'market_making':
                result = self._simulate_market_making_strategy(strategy, historical_data, capital, min_length)
            else:  # rebalancing
                result = self._simulate_rebalancing_strategy(strategy, historical_data, capital, min_length)
            
            return result
            
        except Exception as e:
            logger.error(f"Error simulating strategy {strategy.name}: {e}")
            return self._create_empty_result(strategy)
    
    def _simulate_staking_strategy(self, strategy: TradingStrategy, historical_data: Dict[str, List[MarketData]], capital: float, length: int) -> BacktestResult:
        """Simulate staking strategy"""
        daily_apy = strategy.expected_apy / 365 / 100
        portfolio_values = [capital]
        daily_returns = []
        trade_history = []
        
        current_value = capital
        
        for day in range(1, length):
            # Apply daily staking rewards
            daily_reward = current_value * daily_apy
            current_value += daily_reward
            
            daily_return = (current_value - portfolio_values[-1]) / portfolio_values[-1]
            daily_returns.append(daily_return)
            portfolio_values.append(current_value)
            
            # Record trade every 30 days
            if day % 30 == 0:
                trade_history.append({
                    'day': day,
                    'type': 'staking_reward',
                    'amount': daily_reward * 30,
                    'portfolio_value': current_value
                })
        
        return self._calculate_metrics(strategy, portfolio_values, daily_returns, trade_history)
    
    def _simulate_arbitrage_strategy(self, strategy: TradingStrategy, historical_data: Dict[str, List[MarketData]], capital: float, length: int) -> BacktestResult:
        """Simulate arbitrage strategy"""
        portfolio_values = [capital]
        daily_returns = []
        trade_history = []
        
        current_value = capital
        opportunities_per_day = strategy.parameters.get('opportunities_per_day', 0.1)
        avg_profit_per_trade = strategy.parameters.get('avg_profit_percent', 0.5) / 100
        
        for day in range(1, length):
            # Check for arbitrage opportunities
            if np.random.random() < opportunities_per_day:
                # Simulate arbitrage trade
                trade_amount = current_value * 0.1  # Use 10% of portfolio
                profit = trade_amount * avg_profit_per_trade
                current_value += profit
                
                trade_history.append({
                    'day': day,
                    'type': 'arbitrage',
                    'profit': profit,
                    'portfolio_value': current_value
                })
            
            daily_return = (current_value - portfolio_values[-1]) / portfolio_values[-1]
            daily_returns.append(daily_return)
            portfolio_values.append(current_value)
        
        return self._calculate_metrics(strategy, portfolio_values, daily_returns, trade_history)
    
    def _simulate_market_making_strategy(self, strategy: TradingStrategy, historical_data: Dict[str, List[MarketData]], capital: float, length: int) -> BacktestResult:
        """Simulate market making strategy"""
        portfolio_values = [capital]
        daily_returns = []
        trade_history = []
        
        current_value = capital
        daily_fee_rate = strategy.parameters.get('daily_fee_rate', 0.002)  # 0.2% daily
        
        sol_data = historical_data.get('SOL', [])
        
        for day in range(1, min(length, len(sol_data))):
            # Calculate fees earned from market making
            sol_price_change = abs(sol_data[day].price - sol_data[day-1].price) / sol_data[day-1].price
            
            # Higher volatility = more fees
            volatility_multiplier = 1 + sol_price_change * 10
            daily_fees = current_value * daily_fee_rate * volatility_multiplier
            
            # Impermanent loss (simplified)
            il_factor = strategy.parameters.get('il_factor', 0.1)
            impermanent_loss = current_value * sol_price_change * il_factor
            
            net_daily_profit = daily_fees - impermanent_loss
            current_value += net_daily_profit
            
            if abs(net_daily_profit) > current_value * 0.001:  # Record significant trades
                trade_history.append({
                    'day': day,
                    'type': 'market_making',
                    'fees': daily_fees,
                    'il': impermanent_loss,
                    'net_profit': net_daily_profit,
                    'portfolio_value': current_value
                })
            
            daily_return = (current_value - portfolio_values[-1]) / portfolio_values[-1]
            daily_returns.append(daily_return)
            portfolio_values.append(current_value)
        
        return self._calculate_metrics(strategy, portfolio_values, daily_returns, trade_history)
    
    def _simulate_rebalancing_strategy(self, strategy: TradingStrategy, historical_data: Dict[str, List[MarketData]], capital: float, length: int) -> BacktestResult:
        """Simulate rebalancing strategy"""
        portfolio_values = [capital]
        daily_returns = []
        trade_history = []
        
        # Portfolio allocation
        allocations = strategy.parameters.get('allocations', {'SOL': 0.4, 'ETH': 0.3, 'BTC': 0.2, 'USDC': 0.1})
        rebalance_frequency = strategy.parameters.get('rebalance_days', 30)
        
        portfolio = {}
        for symbol, allocation in allocations.items():
            if symbol in historical_data and historical_data[symbol]:
                initial_price = historical_data[symbol][0].price
                portfolio[symbol] = {
                    'amount': (capital * allocation) / initial_price,
                    'allocation': allocation
                }
        
        for day in range(1, length):
            # Calculate current portfolio value
            current_value = 0
            for symbol, holding in portfolio.items():
                if symbol in historical_data and day < len(historical_data[symbol]):
                    current_price = historical_data[symbol][day].price
                    current_value += holding['amount'] * current_price
                else:
                    current_value += holding['amount']  # Stable value for USDC
            
            # Rebalance periodically
            if day % rebalance_frequency == 0:
                for symbol, holding in portfolio.items():
                    target_value = current_value * holding['allocation']
                    if symbol in historical_data and day < len(historical_data[symbol]):
                        current_price = historical_data[symbol][day].price
                        portfolio[symbol]['amount'] = target_value / current_price
                    
                trade_history.append({
                    'day': day,
                    'type': 'rebalance',
                    'portfolio_value': current_value
                })
            
            daily_return = (current_value - portfolio_values[-1]) / portfolio_values[-1]
            daily_returns.append(daily_return)
            portfolio_values.append(current_value)
        
        return self._calculate_metrics(strategy, portfolio_values, daily_returns, trade_history)
    
    def _calculate_metrics(self, strategy: TradingStrategy, portfolio_values: List[float], daily_returns: List[float], trade_history: List[Dict[str, Any]]) -> BacktestResult:
        """Calculate performance metrics"""
        try:
            if len(portfolio_values) < 2 or len(daily_returns) == 0:
                return self._create_empty_result(strategy)
            
            # Basic metrics
            total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0]
            annualized_return = (1 + total_return) ** (365 / len(daily_returns)) - 1
            volatility = np.std(daily_returns) * np.sqrt(365)
            
            # Risk metrics
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # Max drawdown
            peak = portfolio_values[0]
            max_drawdown = 0
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            # Trade metrics
            positive_returns = [r for r in daily_returns if r > 0]
            win_rate = len(positive_returns) / len(daily_returns) if daily_returns else 0
            
            profit_factor = sum(positive_returns) / abs(sum([r for r in daily_returns if r < 0])) if any(r < 0 for r in daily_returns) else float('inf')
            
            calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else float('inf')
            
            # Sortino ratio
            negative_returns = [r for r in daily_returns if r < 0]
            downside_deviation = np.std(negative_returns) * np.sqrt(365) if negative_returns else 0
            sortino_ratio = annualized_return / downside_deviation if downside_deviation > 0 else float('inf')
            
            return BacktestResult(
                strategy_name=strategy.name,
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                calmar_ratio=calmar_ratio,
                sortino_ratio=sortino_ratio,
                trades_count=len(trade_history),
                avg_trade_duration=1.0,  # Daily strategy
                best_trade=max(daily_returns) if daily_returns else 0,
                worst_trade=min(daily_returns) if daily_returns else 0,
                final_portfolio_value=portfolio_values[-1],
                daily_returns=daily_returns,
                portfolio_values=portfolio_values,
                trade_history=trade_history
            )
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return self._create_empty_result(strategy)
    
    def _create_empty_result(self, strategy: TradingStrategy) -> BacktestResult:
        """Create empty result for failed backtests"""
        return BacktestResult(
            strategy_name=strategy.name,
            total_return=0.0,
            annualized_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            calmar_ratio=0.0,
            sortino_ratio=0.0,
            trades_count=0,
            avg_trade_duration=0.0,
            best_trade=0.0,
            worst_trade=0.0,
            final_portfolio_value=self.initial_capital,
            daily_returns=[],
            portfolio_values=[self.initial_capital],
            trade_history=[]
        )

class StrategySwarmOptimizer:
    """Agent swarm for strategy optimization"""
    
    def __init__(self):
        self.backtester = None
        self.optimization_results = []
        
    async def __aenter__(self):
        self.backtester = await StrategyBacktester().__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.backtester:
            await self.backtester.__aexit__(exc_type, exc_val, exc_tb)
    
    async def optimize_strategy_parameters(self, base_strategy: TradingStrategy, parameter_ranges: Dict[str, Tuple[float, float]], iterations: int = 10) -> List[BacktestResult]:
        """Optimize strategy parameters using swarm intelligence"""
        logger.info(f"Starting parameter optimization for {base_strategy.name}")
        
        optimization_results = []
        
        for i in range(iterations):
            # Generate random parameters within ranges
            optimized_params = {}
            for param, (min_val, max_val) in parameter_ranges.items():
                optimized_params[param] = np.random.uniform(min_val, max_val)
            
            # Create new strategy with optimized parameters
            optimized_strategy = TradingStrategy(
                name=f"{base_strategy.name}_opt_{i}",
                description=f"Optimized version {i} of {base_strategy.description}",
                strategy_type=base_strategy.strategy_type,
                parameters={**base_strategy.parameters, **optimized_params},
                risk_level=base_strategy.risk_level,
                expected_apy=base_strategy.expected_apy,
                capital_allocation=base_strategy.capital_allocation
            )
            
            # Backtest optimized strategy
            result = await self.backtester.run_backtest(optimized_strategy)
            optimization_results.append(result)
            
            logger.info(f"Optimization {i+1}/{iterations}: {result.annualized_return:.2%} return, {result.sharpe_ratio:.2f} Sharpe")
        
        # Sort by Sharpe ratio
        optimization_results.sort(key=lambda x: x.sharpe_ratio, reverse=True)
        
        logger.info(f"Best optimization: {optimization_results[0].sharpe_ratio:.2f} Sharpe ratio")
        return optimization_results
    
    async def run_strategy_comparison(self, strategies: List[TradingStrategy]) -> Dict[str, Any]:
        """Compare multiple strategies"""
        logger.info(f"Comparing {len(strategies)} strategies")
        
        results = {}
        for strategy in strategies:
            result = await self.backtester.run_backtest(strategy)
            results[strategy.name] = result
        
        # Generate comparison report
        comparison = self._generate_comparison_report(results)
        return comparison
    
    def _generate_comparison_report(self, results: Dict[str, BacktestResult]) -> Dict[str, Any]:
        """Generate strategy comparison report"""
        if not results:
            return {}
        
        # Performance summary
        performance_df = pd.DataFrame([
            {
                'Strategy': name,
                'Total Return': f"{result.total_return:.2%}",
                'Annualized Return': f"{result.annualized_return:.2%}",
                'Volatility': f"{result.volatility:.2%}",
                'Sharpe Ratio': f"{result.sharpe_ratio:.2f}",
                'Max Drawdown': f"{result.max_drawdown:.2%}",
                'Win Rate': f"{result.win_rate:.2%}",
                'Final Value': f"${result.final_portfolio_value:,.2f}"
            }
            for name, result in results.items()
        ])
        
        # Find best strategies by different metrics
        best_return = max(results.values(), key=lambda x: x.annualized_return)
        best_sharpe = max(results.values(), key=lambda x: x.sharpe_ratio)
        lowest_drawdown = min(results.values(), key=lambda x: x.max_drawdown)
        
        return {
            'performance_summary': performance_df.to_dict('records'),
            'best_return_strategy': best_return.strategy_name,
            'best_sharpe_strategy': best_sharpe.strategy_name,
            'lowest_drawdown_strategy': lowest_drawdown.strategy_name,
            'detailed_results': {name: asdict(result) for name, result in results.items()}
        }

# Predefined strategies for backtesting
def create_default_strategies() -> List[TradingStrategy]:
    """Create default strategies for testing"""
    strategies = []
    
    # SOL Staking Strategy
    strategies.append(TradingStrategy(
        name="SOL Native Staking",
        description="Stake SOL with native validators for consistent yield",
        strategy_type="staking",
        parameters={"validator_performance": 95.0},
        risk_level="low",
        expected_apy=6.5,
        capital_allocation=40
    ))
    
    # Cross-chain Arbitrage
    strategies.append(TradingStrategy(
        name="Cross-Chain Arbitrage",
        description="Exploit price differences across DEXs and chains",
        strategy_type="arbitrage",
        parameters={
            "opportunities_per_day": 0.2,
            "avg_profit_percent": 0.8,
            "gas_cost_factor": 0.1
        },
        risk_level="medium",
        expected_apy=15.0,
        capital_allocation=25
    ))
    
    # SOL/USDC Market Making
    strategies.append(TradingStrategy(
        name="SOL/USDC Market Making",
        description="Provide liquidity to SOL/USDC pools on Raydium",
        strategy_type="market_making",
        parameters={
            "daily_fee_rate": 0.003,
            "il_factor": 0.15,
            "rebalance_threshold": 0.05
        },
        risk_level="medium",
        expected_apy=12.0,
        capital_allocation=20
    ))
    
    # Multi-Asset Rebalancing
    strategies.append(TradingStrategy(
        name="Multi-Asset Rebalancing",
        description="Systematic rebalancing across SOL, ETH, BTC, USDC",
        strategy_type="rebalancing",
        parameters={
            "allocations": {"SOL": 0.4, "ETH": 0.3, "BTC": 0.2, "USDC": 0.1},
            "rebalance_days": 14,
            "threshold": 0.05
        },
        risk_level="medium",
        expected_apy=8.5,
        capital_allocation=15
    ))
    
    return strategies

async def run_comprehensive_backtest():
    """Run comprehensive backtesting analysis"""
    print("🚀 Starting Comprehensive Strategy Backtesting...")
    print("=" * 80)
    
    async with StrategySwarmOptimizer() as optimizer:
        # Create default strategies
        strategies = create_default_strategies()
        
        print(f"📊 Testing {len(strategies)} strategies:")
        for strategy in strategies:
            print(f"  • {strategy.name} ({strategy.capital_allocation}% allocation)")
        print()
        
        # Run strategy comparison
        comparison_results = await optimizer.run_strategy_comparison(strategies)
        
        # Display results
        print("📈 BACKTEST RESULTS")
        print("=" * 80)
        
        if 'performance_summary' in comparison_results:
            for result in comparison_results['performance_summary']:
                print(f"Strategy: {result['Strategy']}")
                print(f"  Return: {result['Annualized Return']} | Sharpe: {result['Sharpe Ratio']} | Drawdown: {result['Max Drawdown']}")
                print(f"  Win Rate: {result['Win Rate']} | Final Value: {result['Final Value']}")
                print()
        
        print("🏆 BEST PERFORMERS")
        print("=" * 80)
        print(f"Best Return: {comparison_results.get('best_return_strategy', 'N/A')}")
        print(f"Best Sharpe: {comparison_results.get('best_sharpe_strategy', 'N/A')}")
        print(f"Lowest Drawdown: {comparison_results.get('lowest_drawdown_strategy', 'N/A')}")
        print()
        
        # Optimize best strategy
        best_strategy = None
        if strategies:
            best_strategy = strategies[0]  # Start with first strategy
            
            print(f"🔧 OPTIMIZING: {best_strategy.name}")
            print("=" * 80)
            
            # Define parameter ranges for optimization
            parameter_ranges = {}
            if best_strategy.strategy_type == "arbitrage":
                parameter_ranges = {
                    "opportunities_per_day": (0.1, 0.5),
                    "avg_profit_percent": (0.3, 1.5)
                }
            elif best_strategy.strategy_type == "market_making":
                parameter_ranges = {
                    "daily_fee_rate": (0.001, 0.005),
                    "il_factor": (0.05, 0.25)
                }
            
            if parameter_ranges:
                optimizations = await optimizer.optimize_strategy_parameters(
                    best_strategy, parameter_ranges, iterations=5
                )
                
                print("Optimization Results:")
                for i, opt in enumerate(optimizations[:3]):
                    print(f"  #{i+1}: {opt.annualized_return:.2%} return, {opt.sharpe_ratio:.2f} Sharpe")
        
        print("\n✅ Backtesting Complete!")
        return comparison_results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_backtest())
