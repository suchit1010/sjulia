"""
Portfolio Analysis Engine

Core analysis system for DeFi protocols, yield opportunities, and risk assessment.
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from ..utils.logger import portfolio_logger
from ..utils.config import get_config


@dataclass
class ProtocolData:
    """DeFi protocol information."""
    name: str
    tvl: float
    apy: float
    category: str
    risk_score: float
    chain: str
    url: str
    description: str


@dataclass
class YieldOpportunity:
    """Yield farming opportunity."""
    protocol: str
    pair: str
    apy: float
    tvl: float
    risk_score: float
    chain: str
    strategy_type: str
    min_deposit: float
    lockup_period: Optional[int] = None


@dataclass
class ArbitrageOpportunity:
    """Cross-chain arbitrage opportunity."""
    asset: str
    source_exchange: str
    target_exchange: str
    source_price: float
    target_price: float
    profit_percentage: float
    estimated_profit_usd: float
    gas_cost_estimate: float
    net_profit_usd: float
    confidence_score: float


class ProtocolAnalyzer:
    """Analyzes DeFi protocols for investment opportunities."""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
        self.protocols_cache = {}
        self.last_update = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_defi_protocols(self) -> List[ProtocolData]:
        """Fetch DeFi protocol data from various sources."""
        try:
            protocols = []
            
            # Fetch from DeFiLlama
            defi_llama_data = await self._fetch_defillama_protocols()
            protocols.extend(defi_llama_data)
            
            # Add manual high-quality protocols
            protocols.extend(self._get_curated_protocols())
            
            portfolio_logger.info(f"Fetched {len(protocols)} DeFi protocols for analysis")
            return protocols
            
        except Exception as e:
            portfolio_logger.error(f"Error fetching DeFi protocols: {e}")
            return []
    
    async def _fetch_defillama_protocols(self) -> List[ProtocolData]:
        """Fetch protocols from DeFiLlama API."""
        try:
            url = "https://api.llama.fi/protocols"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    protocols = []
                    
                    for item in data[:50]:  # Top 50 protocols
                        if item.get('tvl', 0) > 10_000_000:  # Min $10M TVL
                            protocol = ProtocolData(
                                name=item['name'],
                                tvl=item.get('tvl', 0),
                                apy=self._estimate_apy(item),
                                category=item.get('category', 'Unknown'),
                                risk_score=self._calculate_risk_score(item),
                                chain=item.get('chain', 'Ethereum'),
                                url=item.get('url', ''),
                                description=item.get('description', '')
                            )
                            protocols.append(protocol)
                    
                    return protocols
                    
        except Exception as e:
            portfolio_logger.error(f"Error fetching DeFiLlama data: {e}")
            return []
    
    def _get_curated_protocols(self) -> List[ProtocolData]:
        """Get manually curated high-quality protocols."""
        return [
            ProtocolData(
                name="Uniswap V3",
                tvl=5_000_000_000,
                apy=15.0,
                category="DEX",
                risk_score=0.2,
                chain="Ethereum",
                url="https://app.uniswap.org",
                description="Leading decentralized exchange with concentrated liquidity"
            ),
            ProtocolData(
                name="Aave",
                tvl=12_000_000_000,
                apy=8.5,
                category="Lending",
                risk_score=0.15,
                chain="Ethereum",
                url="https://app.aave.com",
                description="Decentralized lending and borrowing protocol"
            ),
            ProtocolData(
                name="Raydium",
                tvl=800_000_000,
                apy=25.0,
                category="DEX",
                risk_score=0.3,
                chain="Solana",
                url="https://raydium.io",
                description="Automated market maker and liquidity provider on Solana"
            ),
            ProtocolData(
                name="Marinade",
                tvl=1_200_000_000,
                apy=7.2,
                category="Staking",
                risk_score=0.2,
                chain="Solana", 
                url="https://marinade.finance",
                description="Liquid staking protocol for Solana"
            )
        ]
    
    def _estimate_apy(self, protocol_data: Dict) -> float:
        """Estimate APY based on protocol data."""
        # Simple estimation based on category and TVL
        category = protocol_data.get('category', '').lower()
        tvl = protocol_data.get('tvl', 0)
        
        base_apy = {
            'dex': 12.0,
            'lending': 6.0,
            'staking': 8.0,
            'yield': 15.0,
            'derivatives': 20.0
        }.get(category, 10.0)
        
        # Adjust based on TVL (higher TVL = lower risk = lower APY)
        if tvl > 1_000_000_000:
            return base_apy * 0.8
        elif tvl > 100_000_000:
            return base_apy
        else:
            return base_apy * 1.5
    
    def _calculate_risk_score(self, protocol_data: Dict) -> float:
        """Calculate risk score (0 = low risk, 1 = high risk)."""
        tvl = protocol_data.get('tvl', 0)
        
        # Base risk by TVL
        if tvl > 1_000_000_000:
            base_risk = 0.1
        elif tvl > 100_000_000:
            base_risk = 0.3
        else:
            base_risk = 0.6
            
        # Adjust by category
        category = protocol_data.get('category', '').lower()
        category_risk = {
            'lending': 0.0,
            'staking': 0.1,
            'dex': 0.2,
            'yield': 0.3,
            'derivatives': 0.4
        }.get(category, 0.5)
        
        return min(1.0, (base_risk + category_risk) / 2)


class YieldAnalyzer:
    """Analyzes yield farming opportunities across protocols."""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def find_yield_opportunities(self, protocols: List[ProtocolData]) -> List[YieldOpportunity]:
        """Find high-yield opportunities across protocols."""
        opportunities = []
        
        for protocol in protocols:
            # Skip if below minimum yield threshold
            min_yield = self.config.target_assets.get('min_yield', 5.0)
            if protocol.apy < min_yield:
                continue
                
            # Create opportunities based on protocol type
            if protocol.category.lower() == 'dex':
                opportunities.extend(self._create_dex_opportunities(protocol))
            elif protocol.category.lower() == 'lending':
                opportunities.extend(self._create_lending_opportunities(protocol))
            elif protocol.category.lower() == 'staking':
                opportunities.extend(self._create_staking_opportunities(protocol))
                
        # Sort by risk-adjusted returns
        opportunities.sort(
            key=lambda x: x.apy / (1 + x.risk_score), 
            reverse=True
        )
        
        portfolio_logger.info(f"Found {len(opportunities)} yield opportunities")
        return opportunities[:20]  # Top 20 opportunities
    
    def _create_dex_opportunities(self, protocol: ProtocolData) -> List[YieldOpportunity]:
        """Create DEX liquidity providing opportunities."""
        opportunities = []
        
        # Common trading pairs
        pairs = ["ETH/USDC", "SOL/USDC", "BTC/ETH", "USDC/USDT"]
        
        for pair in pairs:
            # Adjust APY based on pair volatility
            pair_multiplier = {
                "ETH/USDC": 1.0,
                "SOL/USDC": 1.2,  # Higher volatility
                "BTC/ETH": 0.8,   # Lower volume
                "USDC/USDT": 0.3  # Stable pair
            }.get(pair, 1.0)
            
            opportunity = YieldOpportunity(
                protocol=protocol.name,
                pair=pair,
                apy=protocol.apy * pair_multiplier,
                tvl=protocol.tvl * 0.1,  # Assume 10% in this pair
                risk_score=protocol.risk_score,
                chain=protocol.chain,
                strategy_type="Liquidity Providing",
                min_deposit=100.0
            )
            opportunities.append(opportunity)
            
        return opportunities
    
    def _create_lending_opportunities(self, protocol: ProtocolData) -> List[YieldOpportunity]:
        """Create lending/borrowing opportunities."""
        opportunities = []
        
        assets = ["ETH", "SOL", "USDC", "USDT"]
        
        for asset in assets:
            # Supply side opportunity
            supply_opportunity = YieldOpportunity(
                protocol=protocol.name,
                pair=f"{asset} Supply",
                apy=protocol.apy,
                tvl=protocol.tvl * 0.25,  # 25% per asset
                risk_score=protocol.risk_score,
                chain=protocol.chain,
                strategy_type="Lending",
                min_deposit=50.0
            )
            opportunities.append(supply_opportunity)
            
        return opportunities
    
    def _create_staking_opportunities(self, protocol: ProtocolData) -> List[YieldOpportunity]:
        """Create staking opportunities."""
        if protocol.chain == "Solana":
            return [YieldOpportunity(
                protocol=protocol.name,
                pair="SOL Staking",
                apy=protocol.apy,
                tvl=protocol.tvl,
                risk_score=protocol.risk_score,
                chain=protocol.chain,
                strategy_type="Staking",
                min_deposit=1.0,
                lockup_period=None  # Liquid staking
            )]
        elif protocol.chain == "Ethereum":
            return [YieldOpportunity(
                protocol=protocol.name,
                pair="ETH Staking",
                apy=protocol.apy,
                tvl=protocol.tvl,
                risk_score=protocol.risk_score,
                chain=protocol.chain,
                strategy_type="Staking",
                min_deposit=0.1,
                lockup_period=None  # Liquid staking
            )]
        
        return []


class RiskAnalyzer:
    """Analyzes portfolio and opportunity risks."""
    
    def __init__(self):
        self.config = get_config()
    
    def assess_portfolio_risk(self, opportunities: List[YieldOpportunity]) -> Dict[str, Any]:
        """Assess overall portfolio risk from selected opportunities."""
        if not opportunities:
            return {"risk_score": 0, "recommendations": []}
        
        # Calculate weighted risk score
        total_tvl = sum(op.tvl for op in opportunities)
        weighted_risk = sum(
            (op.tvl / total_tvl) * op.risk_score 
            for op in opportunities
        )
        
        # Chain diversification risk
        chains = {op.chain for op in opportunities}
        chain_risk = max(0, 0.5 - len(chains) * 0.1)  # Penalty for low diversification
        
        # Protocol concentration risk
        protocols = {}
        for op in opportunities:
            protocols[op.protocol] = protocols.get(op.protocol, 0) + op.tvl
        
        max_protocol_exposure = max(protocols.values()) / total_tvl if total_tvl > 0 else 0
        concentration_risk = max(0, max_protocol_exposure - 0.3)  # Flag if >30% in one protocol
        
        overall_risk = (weighted_risk + chain_risk + concentration_risk) / 3
        
        recommendations = []
        if chain_risk > 0.2:
            recommendations.append("Consider diversifying across more blockchains")
        if concentration_risk > 0.1:
            recommendations.append("Reduce concentration in single protocols")
        if weighted_risk > 0.6:
            recommendations.append("Portfolio contains high-risk opportunities")
        
        return {
            "risk_score": overall_risk,
            "weighted_risk": weighted_risk,
            "chain_risk": chain_risk,
            "concentration_risk": concentration_risk,
            "recommendations": recommendations,
            "chain_distribution": {chain: sum(op.tvl for op in opportunities if op.chain == chain) / total_tvl for chain in chains}
        }
    
    def rank_opportunities(self, opportunities: List[YieldOpportunity]) -> List[YieldOpportunity]:
        """Rank opportunities by risk-adjusted returns."""
        def score_opportunity(op: YieldOpportunity) -> float:
            # Risk-adjusted return with TVL weighting
            risk_adjusted_apy = op.apy / (1 + op.risk_score)
            tvl_factor = min(1.0, op.tvl / 100_000_000)  # Prefer higher TVL up to $100M
            return risk_adjusted_apy * (0.8 + 0.2 * tvl_factor)
        
        ranked = sorted(opportunities, key=score_opportunity, reverse=True)
        portfolio_logger.info(f"Ranked {len(ranked)} opportunities by risk-adjusted returns")
        return ranked


class PortfolioOptimizer:
    """Optimizes portfolio allocation across opportunities."""
    
    def __init__(self):
        self.config = get_config()
        self.risk_analyzer = RiskAnalyzer()
    
    def optimize_allocation(
        self, 
        opportunities: List[YieldOpportunity], 
        target_allocation_usd: float
    ) -> Dict[str, Any]:
        """Optimize portfolio allocation across opportunities."""
        
        if not opportunities:
            return {"allocations": [], "total_expected_apy": 0, "risk_score": 0}
        
        # Rank opportunities
        ranked_opportunities = self.risk_analyzer.rank_opportunities(opportunities)
        
        # Simple optimization: allocate based on risk-adjusted returns
        allocations = []
        remaining_capital = target_allocation_usd
        max_single_allocation = target_allocation_usd * 0.25  # Max 25% per opportunity
        
        for opportunity in ranked_opportunities:
            if remaining_capital <= 0:
                break
                
            # Calculate allocation amount
            allocation_amount = min(
                remaining_capital * 0.2,  # Max 20% per opportunity initially
                max_single_allocation,
                opportunity.min_deposit * 10  # At least 10x minimum
            )
            
            if allocation_amount >= opportunity.min_deposit:
                allocations.append({
                    "opportunity": opportunity,
                    "amount_usd": allocation_amount,
                    "percentage": allocation_amount / target_allocation_usd * 100
                })
                remaining_capital -= allocation_amount
        
        # Calculate portfolio metrics
        total_expected_return = sum(
            alloc["amount_usd"] * alloc["opportunity"].apy / 100
            for alloc in allocations
        )
        total_expected_apy = (total_expected_return / target_allocation_usd * 100) if target_allocation_usd > 0 else 0
        
        # Risk assessment
        allocated_opportunities = [alloc["opportunity"] for alloc in allocations]
        risk_assessment = self.risk_analyzer.assess_portfolio_risk(allocated_opportunities)
        
        return {
            "allocations": allocations,
            "total_allocated_usd": target_allocation_usd - remaining_capital,
            "remaining_capital_usd": remaining_capital,
            "total_expected_apy": total_expected_apy,
            "risk_assessment": risk_assessment,
            "opportunities_selected": len(allocations),
            "diversification": {
                "chains": len({alloc["opportunity"].chain for alloc in allocations}),
                "protocols": len({alloc["opportunity"].protocol for alloc in allocations}),
                "strategies": len({alloc["opportunity"].strategy_type for alloc in allocations})
            }
        }


async def analyze_portfolio_opportunities(target_allocation_usd: float = 10000) -> Dict[str, Any]:
    """Main function to analyze and optimize portfolio opportunities."""
    portfolio_logger.info(f"Starting portfolio analysis for ${target_allocation_usd:,.2f}")
    
    try:
        # Initialize analyzers
        async with ProtocolAnalyzer() as protocol_analyzer:
            async with YieldAnalyzer() as yield_analyzer:
                
                # Fetch and analyze protocols
                protocols = await protocol_analyzer.fetch_defi_protocols()
                
                # Find yield opportunities
                opportunities = await yield_analyzer.find_yield_opportunities(protocols)
                
                # Optimize allocation
                optimizer = PortfolioOptimizer()
                optimization_result = optimizer.optimize_allocation(opportunities, target_allocation_usd)
                
                # Log results
                portfolio_logger.info(
                    f"Portfolio optimization complete",
                    total_opportunities=len(opportunities),
                    selected_opportunities=optimization_result["opportunities_selected"],
                    expected_apy=optimization_result["total_expected_apy"],
                    risk_score=optimization_result["risk_assessment"]["risk_score"]
                )
                
                return {
                    "protocols_analyzed": len(protocols),
                    "opportunities_found": len(opportunities),
                    "optimization_result": optimization_result,
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        portfolio_logger.error(f"Error in portfolio analysis: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    # Test the analysis engine
    asyncio.run(analyze_portfolio_opportunities(10000))
