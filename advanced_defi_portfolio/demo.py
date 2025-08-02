"""
Demo Script for Advanced DeFi Portfolio Manager

Demonstrates the capabilities of the portfolio management system with test data.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.utils.logger import portfolio_logger, log_info, log_error
from src.utils.config import get_config, validate_environment
from src.strategies.portfolio_analysis import analyze_portfolio_opportunities


class PortfolioDemo:
    """Demo class showcasing portfolio management capabilities."""
    
    def __init__(self):
        self.config = get_config()
    
    async def run_portfolio_analysis_demo(self) -> Dict[str, Any]:
        """Demonstrate portfolio analysis capabilities."""
        print("\n🔍 Portfolio Analysis Demo")
        print("=" * 40)
        
        try:
            # Run portfolio analysis
            target_allocation = 10000  # $10,000 demo portfolio
            
            print(f"📊 Analyzing optimal allocation for ${target_allocation:,}")
            print("⏳ Fetching DeFi protocols and opportunities...")
            
            analysis_result = await analyze_portfolio_opportunities(target_allocation)
            
            if "error" in analysis_result:
                print(f"❌ Analysis failed: {analysis_result['error']}")
                return analysis_result
            
            # Display results
            print(f"✅ Analysis completed successfully!")
            print(f"   • Protocols analyzed: {analysis_result.get('protocols_analyzed', 0)}")
            print(f"   • Opportunities found: {analysis_result.get('opportunities_found', 0)}")
            
            optimization = analysis_result.get('optimization_result', {})
            if optimization:
                print(f"\n📈 Portfolio Optimization Results:")
                print(f"   • Total allocated: ${optimization.get('total_allocated_usd', 0):,.2f}")
                print(f"   • Expected APY: {optimization.get('total_expected_apy', 0):.2f}%")
                print(f"   • Risk score: {optimization.get('risk_assessment', {}).get('risk_score', 0):.3f}")
                print(f"   • Opportunities selected: {optimization.get('opportunities_selected', 0)}")
                
                # Show diversification
                diversification = optimization.get('diversification', {})
                print(f"\n🌐 Diversification:")
                print(f"   • Chains: {diversification.get('chains', 0)}")
                print(f"   • Protocols: {diversification.get('protocols', 0)}")
                print(f"   • Strategies: {diversification.get('strategies', 0)}")
                
                # Show top allocations
                allocations = optimization.get('allocations', [])
                if allocations:
                    print(f"\n💰 Top Investment Opportunities:")
                    for i, alloc in enumerate(allocations[:5], 1):
                        opp = alloc['opportunity']
                        print(f"   {i}. {opp.protocol} - {opp.pair}")
                        print(f"      APY: {opp.apy:.2f}% | Amount: ${alloc['amount_usd']:,.2f} | Risk: {opp.risk_score:.3f}")
                
                # Show risk assessment
                risk_assessment = optimization.get('risk_assessment', {})
                recommendations = risk_assessment.get('recommendations', [])
                if recommendations:
                    print(f"\n⚠️ Risk Management Recommendations:")
                    for rec in recommendations:
                        print(f"   • {rec}")
            
            return analysis_result
            
        except Exception as e:
            log_error(f"Demo analysis failed: {e}")
            print(f"❌ Demo failed: {e}")
            return {"error": str(e)}
    
    def simulate_arbitrage_opportunities(self) -> Dict[str, Any]:
        """Simulate cross-chain arbitrage opportunities."""
        print("\n⚡ Cross-Chain Arbitrage Demo")
        print("=" * 40)
        
        # Simulated arbitrage opportunities
        opportunities = [
            {
                "asset": "SOL",
                "source_exchange": "Raydium (Solana)",
                "target_exchange": "Uniswap V3 (Ethereum)",
                "source_price": 98.50,
                "target_price": 99.25,
                "profit_percentage": 0.76,
                "estimated_profit_usd": 76.00,
                "gas_cost_estimate": 25.00,
                "net_profit_usd": 51.00,
                "confidence_score": 0.85
            },
            {
                "asset": "ETH",
                "source_exchange": "Uniswap V3 (Ethereum)",
                "target_exchange": "Serum (Solana)",
                "source_price": 2420.00,
                "target_price": 2435.00,
                "profit_percentage": 0.62,
                "estimated_profit_usd": 150.00,
                "gas_cost_estimate": 35.00,
                "net_profit_usd": 115.00,
                "confidence_score": 0.78
            },
            {
                "asset": "USDC",
                "source_exchange": "Curve (Ethereum)",
                "target_exchange": "Orca (Solana)",
                "source_price": 0.9998,
                "target_price": 1.0012,
                "profit_percentage": 0.14,
                "estimated_profit_usd": 14.00,
                "gas_cost_estimate": 20.00,
                "net_profit_usd": -6.00,
                "confidence_score": 0.92
            }
        ]
        
        print("🔍 Scanning for arbitrage opportunities...")
        print(f"✅ Found {len(opportunities)} potential arbitrage opportunities:\n")
        
        profitable_opportunities = []
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp['asset']} Arbitrage")
            print(f"   Route: {opp['source_exchange']} → {opp['target_exchange']}")
            print(f"   Price Difference: ${opp['source_price']} → ${opp['target_price']}")
            print(f"   Profit: {opp['profit_percentage']:.2f}% (${opp['net_profit_usd']:.2f} net)")
            print(f"   Confidence: {opp['confidence_score']:.0%}")
            
            if opp['net_profit_usd'] > 0:
                print("   ✅ PROFITABLE")
                profitable_opportunities.append(opp)
            else:
                print("   ❌ Not profitable after gas costs")
            print()
        
        print(f"📊 Summary: {len(profitable_opportunities)}/{len(opportunities)} opportunities are profitable")
        
        if profitable_opportunities:
            best_opportunity = max(profitable_opportunities, key=lambda x: x['net_profit_usd'])
            print(f"🏆 Best opportunity: {best_opportunity['asset']} with ${best_opportunity['net_profit_usd']:.2f} net profit")
        
        return {
            "total_opportunities": len(opportunities),
            "profitable_opportunities": len(profitable_opportunities),
            "best_profit": max((opp['net_profit_usd'] for opp in profitable_opportunities), default=0),
            "opportunities": opportunities
        }
    
    def simulate_market_making(self) -> Dict[str, Any]:
        """Simulate market making strategies."""
        print("\n💱 Market Making Strategy Demo")
        print("=" * 40)
        
        pairs = [
            {
                "pair": "SOL/USDC",
                "exchange": "Raydium",
                "current_price": 98.75,
                "bid_spread": 0.15,
                "ask_spread": 0.15,
                "liquidity_provided": 5000,
                "daily_volume": 2500000,
                "estimated_daily_fees": 125.00
            },
            {
                "pair": "ETH/USDC", 
                "exchange": "Uniswap V3",
                "current_price": 2425.00,
                "bid_spread": 0.10,
                "ask_spread": 0.10,
                "liquidity_provided": 10000,
                "daily_volume": 5000000,
                "estimated_daily_fees": 250.00
            },
            {
                "pair": "BTC/ETH",
                "exchange": "Uniswap V3", 
                "current_price": 26.85,
                "bid_spread": 0.20,
                "ask_spread": 0.20,
                "liquidity_provided": 7500,
                "daily_volume": 1500000,
                "estimated_daily_fees": 75.00
            }
        ]
        
        print("📊 Market Making Analysis:")
        print()
        
        total_liquidity = 0
        total_daily_fees = 0
        
        for i, pair in enumerate(pairs, 1):
            bid_price = pair['current_price'] * (1 - pair['bid_spread'] / 100)
            ask_price = pair['current_price'] * (1 + pair['ask_spread'] / 100)
            
            print(f"{i}. {pair['pair']} on {pair['exchange']}")
            print(f"   Current Price: ${pair['current_price']:.2f}")
            print(f"   Bid/Ask: ${bid_price:.2f} / ${ask_price:.2f}")
            print(f"   Spread: {pair['bid_spread'] + pair['ask_spread']:.2f}%")
            print(f"   Liquidity Provided: ${pair['liquidity_provided']:,}")
            print(f"   Daily Volume: ${pair['daily_volume']:,}")
            print(f"   Est. Daily Fees: ${pair['estimated_daily_fees']:.2f}")
            print()
            
            total_liquidity += pair['liquidity_provided']
            total_daily_fees += pair['estimated_daily_fees']
        
        annual_fees = total_daily_fees * 365
        annual_yield = (annual_fees / total_liquidity) * 100 if total_liquidity > 0 else 0
        
        print(f"💰 Portfolio Summary:")
        print(f"   Total Liquidity: ${total_liquidity:,}")
        print(f"   Daily Fees: ${total_daily_fees:.2f}")
        print(f"   Annual Fees: ${annual_fees:,.2f}")
        print(f"   Annual Yield: {annual_yield:.2f}%")
        
        return {
            "total_liquidity": total_liquidity,
            "daily_fees": total_daily_fees,
            "annual_yield": annual_yield,
            "pairs": pairs
        }
    
    def simulate_staking_optimization(self) -> Dict[str, Any]:
        """Simulate staking optimization across protocols."""
        print("\n🥩 Staking Optimization Demo")
        print("=" * 40)
        
        staking_options = [
            {
                "protocol": "Marinade Finance",
                "asset": "SOL",
                "apy": 7.2,
                "tvl": 1200000000,
                "risk_score": 0.2,
                "lockup_period": None,
                "min_stake": 1.0,
                "validator_count": 400
            },
            {
                "protocol": "Lido",
                "asset": "ETH", 
                "apy": 5.8,
                "tvl": 32000000000,
                "risk_score": 0.15,
                "lockup_period": None,
                "min_stake": 0.1,
                "validator_count": 1200
            },
            {
                "protocol": "Jito",
                "asset": "SOL",
                "apy": 8.1,
                "tvl": 850000000,
                "risk_score": 0.25,
                "lockup_period": None,
                "min_stake": 1.0,
                "validator_count": 150
            },
            {
                "protocol": "Native Solana",
                "asset": "SOL",
                "apy": 6.5,
                "tvl": 400000000000,
                "risk_score": 0.1,
                "lockup_period": "1 epoch",
                "min_stake": 1.0,
                "validator_count": 1500
            }
        ]
        
        print("🔍 Analyzing staking opportunities:")
        print()
        
        target_stake = 5000  # $5,000 to stake
        
        for i, option in enumerate(staking_options, 1):
            risk_adjusted_apy = option['apy'] / (1 + option['risk_score'])
            
            print(f"{i}. {option['protocol']} ({option['asset']})")
            print(f"   APY: {option['apy']:.1f}% | Risk Score: {option['risk_score']:.2f}")
            print(f"   Risk-Adjusted APY: {risk_adjusted_apy:.1f}%")
            print(f"   TVL: ${option['tvl']:,}")
            print(f"   Validators: {option['validator_count']:,}")
            print(f"   Lockup: {option['lockup_period'] or 'None (Liquid Staking)'}")
            print()
        
        # Find optimal allocation
        sorted_options = sorted(staking_options, key=lambda x: x['apy'] / (1 + x['risk_score']), reverse=True)
        
        print("🏆 Recommended Allocation:")
        allocation_percentages = [40, 30, 20, 10]  # Diversified allocation
        
        total_expected_return = 0
        
        for i, (option, percentage) in enumerate(zip(sorted_options, allocation_percentages)):
            allocation_amount = target_stake * (percentage / 100)
            annual_return = allocation_amount * (option['apy'] / 100)
            total_expected_return += annual_return
            
            print(f"   {i+1}. {option['protocol']}: {percentage}% (${allocation_amount:,.0f})")
            print(f"      Expected Annual Return: ${annual_return:.2f}")
        
        weighted_apy = (total_expected_return / target_stake) * 100
        
        print(f"\n💰 Portfolio Summary:")
        print(f"   Total Staked: ${target_stake:,}")
        print(f"   Weighted APY: {weighted_apy:.2f}%")
        print(f"   Expected Annual Return: ${total_expected_return:.2f}")
        print(f"   Diversification: {len(sorted_options)} protocols")
        
        return {
            "total_staked": target_stake,
            "weighted_apy": weighted_apy,
            "expected_annual_return": total_expected_return,
            "allocation": list(zip(sorted_options, allocation_percentages))
        }
    
    async def run_full_demo(self) -> Dict[str, Any]:
        """Run the complete portfolio management demo."""
        print("🚀 Advanced DeFi Portfolio Manager - DEMO")
        print("=" * 50)
        print("Powered by JuliaOS AI Agents & Swarm Intelligence")
        print("=" * 50)
        
        demo_results = {}
        
        try:
            # Environment validation
            print("\n🔧 Environment Validation")
            print("=" * 30)
            
            validation = validate_environment()
            print(f"✅ Configuration valid: {validation['valid']}")
            
            if validation['warnings']:
                print("⚠️ Warnings:")
                for warning in validation['warnings']:
                    print(f"   • {warning}")
            
            if not validation['valid']:
                print("❌ Configuration issues:")
                for issue in validation['issues']:
                    print(f"   • {issue}")
                return {"error": "Configuration validation failed"}
            
            # Run demos
            demo_results['portfolio_analysis'] = await self.run_portfolio_analysis_demo()
            demo_results['arbitrage'] = self.simulate_arbitrage_opportunities()
            demo_results['market_making'] = self.simulate_market_making()
            demo_results['staking'] = self.simulate_staking_optimization()
            
            # Summary
            print("\n📊 Demo Summary")
            print("=" * 30)
            
            if 'error' not in demo_results['portfolio_analysis']:
                opt_result = demo_results['portfolio_analysis'].get('optimization_result', {})
                print(f"🔍 Portfolio Analysis:")
                print(f"   • Expected APY: {opt_result.get('total_expected_apy', 0):.2f}%")
                print(f"   • Risk Score: {opt_result.get('risk_assessment', {}).get('risk_score', 0):.3f}")
            
            print(f"⚡ Arbitrage Opportunities: {demo_results['arbitrage']['profitable_opportunities']}")
            print(f"💱 Market Making APY: {demo_results['market_making']['annual_yield']:.2f}%")
            print(f"🥩 Staking APY: {demo_results['staking']['weighted_apy']:.2f}%")
            
            print("\n✅ Demo completed successfully!")
            print("\n🎯 Next Steps:")
            print("   1. Set up your API keys in .env file")
            print("   2. Run: python main.py")
            print("   3. Monitor your portfolio through the dashboard")
            print("   4. Customize strategies for your risk tolerance")
            
            return demo_results
            
        except Exception as e:
            log_error(f"Demo failed: {e}")
            print(f"❌ Demo failed: {e}")
            return {"error": str(e)}


async def main():
    """Main demo entry point."""
    demo = PortfolioDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
