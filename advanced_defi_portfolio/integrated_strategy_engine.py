#!/usr/bin/env python3
"""
Integrated Strategy Engine with Real-Time Backtesting
Combines real portfolio analysis with strategy backtesting and optimization

Features:
- Real-time strategy execution based on backtesting results
- Dynamic strategy switching based on market conditions
- Live performance tracking vs backtested expectations
- Agent swarm coordination for optimal strategy selection
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import logging
from strategy_backtester import StrategySwarmOptimizer, create_default_strategies, TradingStrategy, BacktestResult

logger = logging.getLogger(__name__)

class LiveStrategyEngine:
    """Integrates backtesting with live trading decisions"""
    
    def __init__(self, portfolio_value: float):
        self.portfolio_value = portfolio_value
        self.optimizer = None
        self.active_strategies = []
        self.strategy_performance = {}
        self.backtest_results = {}
        
    async def __aenter__(self):
        self.optimizer = await StrategySwarmOptimizer().__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.optimizer:
            await self.optimizer.__aexit__(exc_type, exc_val, exc_tb)
    
    async def initialize_strategies(self) -> Dict[str, Any]:
        """Initialize and backtest all strategies"""
        logger.info("Initializing strategy engine with backtesting...")
        
        # Create strategies adapted to current portfolio
        strategies = self._create_portfolio_adapted_strategies()
        
        # Run comprehensive backtesting
        backtest_results = await self.optimizer.run_strategy_comparison(strategies)
        self.backtest_results = backtest_results
        
        # Select best strategies for live execution
        self.active_strategies = self._select_optimal_strategies(strategies, backtest_results)
        
        return {
            'total_strategies_tested': len(strategies),
            'active_strategies_selected': len(self.active_strategies),
            'backtest_results': backtest_results,
            'portfolio_allocation': self._calculate_portfolio_allocation()
        }
    
    def _create_portfolio_adapted_strategies(self) -> List[TradingStrategy]:
        """Create strategies adapted to current portfolio size"""
        base_strategies = create_default_strategies()
        adapted_strategies = []
        
        for strategy in base_strategies:
            # Adapt strategy parameters based on portfolio size
            adapted_params = strategy.parameters.copy()
            
            if self.portfolio_value < 1000:
                # Small portfolio: focus on low-cost strategies
                if strategy.strategy_type == "staking":
                    adapted_params["min_stake_amount"] = 50
                elif strategy.strategy_type == "arbitrage":
                    adapted_params["min_trade_size"] = 20
                    adapted_params["gas_optimization"] = True
            elif self.portfolio_value > 10000:
                # Large portfolio: can handle more complex strategies
                if strategy.strategy_type == "market_making":
                    adapted_params["position_size_multiplier"] = 2.0
                elif strategy.strategy_type == "arbitrage":
                    adapted_params["parallel_opportunities"] = True
            
            # Adjust capital allocation based on portfolio size
            if self.portfolio_value < 500:
                # Conservative allocation for small portfolios
                allocation = min(strategy.capital_allocation, 25)
            else:
                allocation = strategy.capital_allocation
            
            adapted_strategy = TradingStrategy(
                name=strategy.name,
                description=strategy.description,
                strategy_type=strategy.strategy_type,
                parameters=adapted_params,
                risk_level=strategy.risk_level,
                expected_apy=strategy.expected_apy,
                capital_allocation=allocation
            )
            
            adapted_strategies.append(adapted_strategy)
        
        return adapted_strategies
    
    def _select_optimal_strategies(self, strategies: List[TradingStrategy], backtest_results: Dict[str, Any]) -> List[TradingStrategy]:
        """Select optimal strategies based on backtest results"""
        if 'detailed_results' not in backtest_results:
            return strategies[:2]  # Default to first 2 strategies
        
        # Score strategies based on multiple criteria
        strategy_scores = {}
        
        for strategy_name, result_dict in backtest_results['detailed_results'].items():
            # Convert dict back to BacktestResult for easier access
            result = BacktestResult(**result_dict)
            
            # Multi-criteria scoring
            return_score = result.annualized_return * 100  # Convert to percentage
            risk_score = (1 - result.max_drawdown) * 100
            consistency_score = result.win_rate * 100
            efficiency_score = result.sharpe_ratio * 20
            
            # Weight the scores based on portfolio size
            if self.portfolio_value < 1000:
                # Small portfolio: prioritize consistency and low risk
                total_score = (return_score * 0.3 + risk_score * 0.4 + 
                             consistency_score * 0.2 + efficiency_score * 0.1)
            else:
                # Larger portfolio: can handle more risk for returns
                total_score = (return_score * 0.4 + risk_score * 0.2 + 
                             consistency_score * 0.2 + efficiency_score * 0.2)
            
            strategy_scores[strategy_name] = total_score
        
        # Sort strategies by score
        sorted_strategies = sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select top strategies (max 3)
        selected_strategy_names = [name for name, score in sorted_strategies[:3]]
        selected_strategies = [s for s in strategies if s.name in selected_strategy_names]
        
        logger.info(f"Selected strategies: {[s.name for s in selected_strategies]}")
        return selected_strategies
    
    def _calculate_portfolio_allocation(self) -> Dict[str, float]:
        """Calculate optimal portfolio allocation across selected strategies"""
        if not self.active_strategies:
            return {}
        
        allocation = {}
        total_allocation = 0
        
        for strategy in self.active_strategies:
            # Get backtest results for allocation optimization
            if strategy.name in self.backtest_results.get('detailed_results', {}):
                result_dict = self.backtest_results['detailed_results'][strategy.name]
                result = BacktestResult(**result_dict)
                
                # Allocate based on risk-adjusted returns
                risk_adjusted_return = result.annualized_return / max(result.volatility, 0.01)
                base_allocation = min(strategy.capital_allocation, 40)  # Max 40% per strategy
                
                # Adjust allocation based on performance
                if risk_adjusted_return > 0.5:  # Good risk-adjusted return
                    final_allocation = base_allocation * 1.2
                elif risk_adjusted_return < 0.1:  # Poor risk-adjusted return
                    final_allocation = base_allocation * 0.6
                else:
                    final_allocation = base_allocation
                
                allocation[strategy.name] = min(final_allocation, 40)
                total_allocation += allocation[strategy.name]
        
        # Normalize to ensure total doesn't exceed 100%
        if total_allocation > 100:
            for strategy_name in allocation:
                allocation[strategy_name] = (allocation[strategy_name] / total_allocation) * 90  # Leave 10% cash
        
        return allocation
    
    async def generate_live_recommendations(self) -> List[Dict[str, Any]]:
        """Generate real-time strategy recommendations based on backtesting"""
        recommendations = []
        
        for strategy in self.active_strategies:
            if strategy.name in self.backtest_results.get('detailed_results', {}):
                result_dict = self.backtest_results['detailed_results'][strategy.name]
                result = BacktestResult(**result_dict)
                
                # Calculate position size
                allocation_pct = self._calculate_portfolio_allocation().get(strategy.name, 0)
                position_size = self.portfolio_value * (allocation_pct / 100)
                
                recommendation = {
                    'strategy_name': strategy.name,
                    'strategy_type': strategy.strategy_type,
                    'action': self._get_strategy_action(strategy),
                    'position_size': position_size,
                    'expected_apy': strategy.expected_apy,
                    'backtested_return': result.annualized_return,
                    'risk_level': strategy.risk_level,
                    'max_drawdown': result.max_drawdown,
                    'sharpe_ratio': result.sharpe_ratio,
                    'confidence_score': self._calculate_confidence_score(result),
                    'execution_priority': self._calculate_execution_priority(strategy, result),
                    'parameters': strategy.parameters
                }
                
                recommendations.append(recommendation)
        
        # Sort by execution priority
        recommendations.sort(key=lambda x: x['execution_priority'], reverse=True)
        return recommendations
    
    def _get_strategy_action(self, strategy: TradingStrategy) -> str:
        """Get specific action for strategy type"""
        actions = {
            'staking': f"Stake {strategy.parameters.get('min_stake_amount', 50)} worth in {strategy.name}",
            'arbitrage': f"Monitor for arbitrage opportunities with {strategy.parameters.get('avg_profit_percent', 0.5)}% target profit",
            'market_making': f"Provide liquidity with {strategy.parameters.get('daily_fee_rate', 0.003)*100:.2f}% daily fee target",
            'rebalancing': f"Rebalance portfolio every {strategy.parameters.get('rebalance_days', 14)} days"
        }
        return actions.get(strategy.strategy_type, f"Execute {strategy.name} strategy")
    
    def _calculate_confidence_score(self, result: BacktestResult) -> float:
        """Calculate confidence score based on backtest results"""
        # Factors: win rate, consistency, Sharpe ratio, number of trades
        win_rate_score = result.win_rate
        sharpe_score = min(result.sharpe_ratio / 2.0, 1.0)  # Normalize Sharpe
        consistency_score = 1 - result.max_drawdown  # Lower drawdown = higher consistency
        trade_count_score = min(result.trades_count / 100, 1.0)  # More trades = more data
        
        confidence = (win_rate_score * 0.3 + sharpe_score * 0.3 + 
                     consistency_score * 0.3 + trade_count_score * 0.1)
        
        return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _calculate_execution_priority(self, strategy: TradingStrategy, result: BacktestResult) -> float:
        """Calculate execution priority for strategy"""
        # Higher priority = better risk-adjusted returns + lower complexity
        return_priority = result.annualized_return * 10
        risk_priority = (1 - result.max_drawdown) * 5
        
        # Strategy type complexity adjustment
        complexity_adjustment = {
            'staking': 1.2,      # Simple, reliable
            'arbitrage': 0.8,    # Complex, requires timing
            'market_making': 0.9, # Medium complexity
            'rebalancing': 1.0   # Medium complexity
        }
        
        complexity_factor = complexity_adjustment.get(strategy.strategy_type, 1.0)
        
        return (return_priority + risk_priority) * complexity_factor

async def create_integrated_analysis() -> Dict[str, Any]:
    """Create integrated analysis combining real portfolio with backtesting"""
    print("🔬 Starting Integrated Portfolio Analysis with Backtesting...")
    print("=" * 80)
    
    # Simulate current portfolio value (in real implementation, get from portfolio analyzer)
    portfolio_value = 2002.69  # From your actual portfolio
    
    async with LiveStrategyEngine(portfolio_value) as engine:
        # Initialize strategies with backtesting
        initialization_results = await engine.initialize_strategies()
        
        print(f"📊 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"📈 Strategies Tested: {initialization_results['total_strategies_tested']}")
        print(f"🎯 Active Strategies: {initialization_results['active_strategies_selected']}")
        print()
        
        # Generate live recommendations
        recommendations = await engine.generate_live_recommendations()
        
        print("🎯 BACKTESTED STRATEGY RECOMMENDATIONS")
        print("=" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['strategy_name']}")
            print(f"   Action: {rec['action']}")
            print(f"   Position Size: ${rec['position_size']:,.2f}")
            print(f"   Expected APY: {rec['expected_apy']:.1f}% | Backtested: {rec['backtested_return']*100:.1f}%")
            print(f"   Risk Level: {rec['risk_level']} | Max Drawdown: {rec['max_drawdown']*100:.1f}%")
            print(f"   Sharpe Ratio: {rec['sharpe_ratio']:.2f} | Confidence: {rec['confidence_score']*100:.0f}%")
            print(f"   Priority Score: {rec['execution_priority']:.1f}")
            print()
        
        print("📋 PORTFOLIO ALLOCATION (Based on Backtesting)")
        print("=" * 80)
        allocation = initialization_results['portfolio_allocation']
        allocated_total = 0
        
        for strategy_name, allocation_pct in allocation.items():
            allocated_amount = portfolio_value * (allocation_pct / 100)
            allocated_total += allocation_pct
            print(f"{strategy_name}: {allocation_pct:.1f}% (${allocated_amount:,.2f})")
        
        cash_pct = 100 - allocated_total
        cash_amount = portfolio_value * (cash_pct / 100)
        print(f"Cash Reserve: {cash_pct:.1f}% (${cash_amount:,.2f})")
        print()
        
        # Performance comparison
        if 'backtest_results' in initialization_results:
            backtest_data = initialization_results['backtest_results']
            
            print("📈 BACKTESTING PERFORMANCE SUMMARY")
            print("=" * 80)
            print(f"Best Return Strategy: {backtest_data.get('best_return_strategy', 'N/A')}")
            print(f"Best Sharpe Strategy: {backtest_data.get('best_sharpe_strategy', 'N/A')}")
            print(f"Lowest Risk Strategy: {backtest_data.get('lowest_drawdown_strategy', 'N/A')}")
        
        return {
            'portfolio_value': portfolio_value,
            'strategies': initialization_results,
            'recommendations': recommendations,
            'allocation': allocation
        }

if __name__ == "__main__":
    asyncio.run(create_integrated_analysis())
