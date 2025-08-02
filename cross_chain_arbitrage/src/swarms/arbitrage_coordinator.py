"""
Arbitrage Swarm Coordinator - Coordinates multiple agents for cross-chain arbitrage
"""
import asyncio
import json
import time
from typing import Dict, List, Optional
from loguru import logger
import os
from dotenv import load_dotenv

# Import JuliaOS components
import juliaos
from juliaos import Agent, AgentBlueprint, AgentState

# Import our agents
from ..agents.solana_price_agent import SolanaPriceAgent, create_solana_agent
from ..agents.ethereum_price_agent import EthereumPriceAgent, create_ethereum_agent
from ..agents.arbitrage_executor import ArbitrageExecutor, create_arbitrage_executor

load_dotenv()

class ArbitrageSwarmCoordinator:
    """
    Swarm coordinator that manages multiple agents for cross-chain arbitrage
    Uses JuliaOS swarm functionality to coordinate agent activities
    """
    
    def __init__(self, connection: juliaos.JuliaOSConnection):
        self.connection = connection
        self.swarm_id = "arbitrage-swarm"
        self.swarm_name = "Cross-Chain Arbitrage Swarm"
        
        # Agent instances
        self.solana_agent: Optional[SolanaPriceAgent] = None
        self.ethereum_agent: Optional[EthereumPriceAgent] = None
        self.executor: Optional[ArbitrageExecutor] = None
        
        # Swarm state
        self.is_running = False
        self.coordination_interval = 5  # seconds
        self.price_data_cache = {}
        self.arbitrage_history = []
        
        # JuliaOS Swarm (we'll use the Python wrapper when available)
        self.juliaos_swarm = None
        
        # Statistics
        self.stats = {
            "total_evaluations": 0,
            "profitable_opportunities": 0,
            "executed_trades": 0,
            "total_profit": 0.0,
            "start_time": None
        }
    
    async def initialize_swarm(self):
        """Initialize the swarm and all agents"""
        try:
            logger.info("🚀 Initializing Cross-Chain Arbitrage Swarm...")
            
            # Create individual agents
            self.solana_agent = await create_solana_agent(self.connection)
            self.ethereum_agent = await create_ethereum_agent(self.connection)
            self.executor = await create_arbitrage_executor(self.connection)
            
            # In a full JuliaOS implementation, we would create a swarm
            # and add these agents to it using the swarm API
            # For now, we'll coordinate them directly
            
            logger.info("✅ All agents initialized successfully")
            
            # Start price monitoring agents
            asyncio.create_task(self.solana_agent.start_monitoring())
            asyncio.create_task(self.ethereum_agent.start_monitoring())
            
            logger.info("✅ Price monitoring started on both chains")
            
            self.stats["start_time"] = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing swarm: {e}")
            return False
    
    async def start_coordination(self):
        """Start the swarm coordination loop"""
        if not all([self.solana_agent, self.ethereum_agent, self.executor]):
            raise ValueError("Swarm not properly initialized")
        
        self.is_running = True
        logger.info("🐝 Starting swarm coordination...")
        
        while self.is_running:
            try:
                await self._coordination_cycle()
                await asyncio.sleep(self.coordination_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in coordination cycle: {e}")
                await asyncio.sleep(1)  # Short delay on error
    
    async def _coordination_cycle(self):
        """Execute one coordination cycle"""
        try:
            # Collect price data from both agents
            solana_price = self.solana_agent.get_current_price()
            ethereum_price = self.ethereum_agent.get_current_price()
            
            # Check if data is fresh enough (within last 30 seconds)
            current_time = time.time()
            solana_age = solana_price.get("age_seconds", float('inf'))
            ethereum_age = ethereum_price.get("age_seconds", float('inf'))
            
            if solana_age > 30 or ethereum_age > 30:
                logger.debug("⏰ Waiting for fresh price data...")
                return
            
            # Update cache
            self.price_data_cache = {
                "solana": solana_price,
                "ethereum": ethereum_price,
                "last_update": current_time
            }
            
            # Perform swarm intelligence coordination
            coordination_result = await self._perform_swarm_coordination(solana_price, ethereum_price)
            
            # Execute decision if profitable
            if coordination_result.get("action") == "execute":
                execution_result = await self.executor.process_arbitrage_signal(
                    solana_price, ethereum_price
                )
                
                # Update statistics
                self._update_stats(coordination_result, execution_result)
                
                # Store in history
                self.arbitrage_history.append({
                    "timestamp": current_time,
                    "prices": self.price_data_cache.copy(),
                    "coordination": coordination_result,
                    "execution": execution_result
                })
                
                # Keep history manageable
                if len(self.arbitrage_history) > 100:
                    self.arbitrage_history = self.arbitrage_history[-50:]
            
            self.stats["total_evaluations"] += 1
            
        except Exception as e:
            logger.error(f"❌ Error in coordination cycle: {e}")
    
    async def _perform_swarm_coordination(self, solana_price: Dict, ethereum_price: Dict) -> Dict:
        """
        Perform swarm intelligence coordination to make arbitrage decisions
        This simulates JuliaOS swarm consensus algorithms
        """
        try:
            # In a full JuliaOS implementation, this would use swarm optimization
            # algorithms like Particle Swarm Optimization (PSO) or Differential Evolution
            
            # Calculate basic metrics
            sol_price = solana_price.get("price", 0)
            eth_price = ethereum_price.get("price", 0)
            
            if sol_price <= 0 or eth_price <= 0:
                return {"action": "wait", "reason": "Invalid price data"}
            
            # Calculate price spread
            price_spread = abs(eth_price - sol_price)
            spread_pct = price_spread / min(sol_price, eth_price)
            
            # Multi-agent consensus simulation
            agents_consensus = await self._simulate_agent_consensus(solana_price, ethereum_price)
            
            # Risk assessment
            risk_assessment = await self._assess_market_risk(solana_price, ethereum_price)
            
            # Swarm decision making
            swarm_decision = await self._make_swarm_decision(
                spread_pct, agents_consensus, risk_assessment
            )
            
            coordination_result = {
                "action": swarm_decision["action"],
                "confidence": swarm_decision["confidence"],
                "reasoning": swarm_decision["reasoning"],
                "metrics": {
                    "price_spread": price_spread,
                    "spread_pct": spread_pct,
                    "sol_price": sol_price,
                    "eth_price": eth_price
                },
                "consensus": agents_consensus,
                "risk": risk_assessment,
                "timestamp": time.time()
            }
            
            # Log decision
            action_emoji = {"execute": "⚡", "wait": "⏸️", "monitor": "👀"}.get(swarm_decision["action"], "❓")
            logger.info(f"{action_emoji} Swarm Decision: {swarm_decision['action'].upper()} | "
                       f"Spread: {spread_pct:.2%} | Confidence: {swarm_decision['confidence']:.2f}")
            
            return coordination_result
            
        except Exception as e:
            logger.error(f"❌ Error in swarm coordination: {e}")
            return {"action": "wait", "reason": f"Coordination error: {e}"}
    
    async def _simulate_agent_consensus(self, solana_price: Dict, ethereum_price: Dict) -> Dict:
        """Simulate multi-agent consensus for arbitrage decision"""
        try:
            # Simulate different agent "opinions"
            agents_votes = []
            
            # Agent 1: Conservative (higher threshold)
            conservative_threshold = 0.03  # 3%
            conservative_vote = self._calculate_vote(solana_price, ethereum_price, conservative_threshold)
            agents_votes.append({"agent": "conservative", "vote": conservative_vote, "weight": 0.3})
            
            # Agent 2: Aggressive (lower threshold)
            aggressive_threshold = 0.015  # 1.5%
            aggressive_vote = self._calculate_vote(solana_price, ethereum_price, aggressive_threshold)
            agents_votes.append({"agent": "aggressive", "vote": aggressive_vote, "weight": 0.3})
            
            # Agent 3: Risk-aware (considers gas and volatility)
            risk_aware_vote = self._calculate_risk_aware_vote(solana_price, ethereum_price)
            agents_votes.append({"agent": "risk_aware", "vote": risk_aware_vote, "weight": 0.4})
            
            # Calculate weighted consensus
            total_weight = sum(vote["weight"] for vote in agents_votes)
            weighted_score = sum(vote["vote"] * vote["weight"] for vote in agents_votes) / total_weight
            
            consensus = {
                "votes": agents_votes,
                "weighted_score": weighted_score,
                "consensus_level": min(weighted_score, 1.0),
                "agreement": "strong" if weighted_score > 0.7 else "moderate" if weighted_score > 0.4 else "weak"
            }
            
            return consensus
            
        except Exception as e:
            logger.error(f"❌ Error in agent consensus: {e}")
            return {"votes": [], "weighted_score": 0.0, "consensus_level": 0.0, "agreement": "error"}
    
    def _calculate_vote(self, solana_price: Dict, ethereum_price: Dict, threshold: float) -> float:
        """Calculate an agent's vote based on threshold"""
        try:
            sol_price = solana_price.get("price", 0)
            eth_price = ethereum_price.get("price", 0)
            
            if sol_price <= 0 or eth_price <= 0:
                return 0.0
            
            spread_pct = abs(eth_price - sol_price) / min(sol_price, eth_price)
            
            if spread_pct > threshold:
                # Strong vote if spread is significantly above threshold
                return min(1.0, spread_pct / threshold)
            else:
                # Weak vote proportional to how close we are to threshold
                return max(0.0, spread_pct / threshold)
                
        except Exception:
            return 0.0
    
    def _calculate_risk_aware_vote(self, solana_price: Dict, ethereum_price: Dict) -> float:
        """Calculate risk-aware vote considering gas and volatility"""
        try:
            base_vote = self._calculate_vote(solana_price, ethereum_price, 0.02)  # 2% threshold
            
            # Adjust for gas costs
            gas_info = ethereum_price.get("gas_info", {})
            gas_price_gwei = gas_info.get("gas_price_gwei", 20)
            
            # Penalize high gas prices
            if gas_price_gwei > 50:  # High gas
                gas_penalty = 0.5
            elif gas_price_gwei > 30:  # Medium gas
                gas_penalty = 0.7
            else:  # Low gas
                gas_penalty = 1.0
            
            # Adjust for price age (prefer fresher data)
            sol_age = solana_price.get("age_seconds", 0)
            eth_age = ethereum_price.get("age_seconds", 0)
            max_age = max(sol_age, eth_age)
            
            age_penalty = 1.0 if max_age < 15 else 0.8 if max_age < 30 else 0.5
            
            risk_adjusted_vote = base_vote * gas_penalty * age_penalty
            
            return min(1.0, risk_adjusted_vote)
            
        except Exception:
            return 0.0
    
    async def _assess_market_risk(self, solana_price: Dict, ethereum_price: Dict) -> Dict:
        """Assess current market risk factors"""
        try:
            risk_factors = []
            risk_score = 0.0
            
            # Gas price risk
            gas_info = ethereum_price.get("gas_info", {})
            gas_price = gas_info.get("gas_price_gwei", 20)
            
            if gas_price > 50:
                risk_factors.append("High gas prices")
                risk_score += 0.3
            elif gas_price > 30:
                risk_factors.append("Elevated gas prices")
                risk_score += 0.1
            
            # Data freshness risk
            sol_age = solana_price.get("age_seconds", 0)
            eth_age = ethereum_price.get("age_seconds", 0)
            
            if max(sol_age, eth_age) > 20:
                risk_factors.append("Stale price data")
                risk_score += 0.2
            
            # Execution time risk (simulated)
            current_hour = time.localtime().tm_hour
            if current_hour < 6 or current_hour > 22:  # Off-hours
                risk_factors.append("Off-hours execution")
                risk_score += 0.1
            
            risk_level = "high" if risk_score > 0.4 else "medium" if risk_score > 0.2 else "low"
            
            return {
                "risk_score": min(1.0, risk_score),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "gas_price_gwei": gas_price
            }
            
        except Exception as e:
            logger.error(f"❌ Error assessing risk: {e}")
            return {"risk_score": 1.0, "risk_level": "unknown", "risk_factors": ["Assessment error"]}
    
    async def _make_swarm_decision(self, spread_pct: float, consensus: Dict, risk: Dict) -> Dict:
        """Make final swarm decision based on all factors"""
        try:
            consensus_score = consensus.get("consensus_level", 0.0)
            risk_score = risk.get("risk_score", 1.0)
            
            # Calculate decision score
            decision_score = consensus_score * (1.0 - risk_score) * min(1.0, spread_pct / 0.02)
            
            # Make decision
            if decision_score > 0.7 and spread_pct > 0.02:
                action = "execute"
                confidence = decision_score
                reasoning = f"Strong consensus ({consensus_score:.2f}) with acceptable risk ({risk_score:.2f})"
            elif decision_score > 0.4 and spread_pct > 0.015:
                action = "monitor"
                confidence = decision_score
                reasoning = f"Moderate opportunity, monitoring for better conditions"
            else:
                action = "wait"
                confidence = 1.0 - decision_score
                reasoning = f"Insufficient profit or high risk (consensus: {consensus_score:.2f}, risk: {risk_score:.2f})"
            
            return {
                "action": action,
                "confidence": confidence,
                "reasoning": reasoning,
                "decision_score": decision_score
            }
            
        except Exception as e:
            logger.error(f"❌ Error making decision: {e}")
            return {"action": "wait", "confidence": 0.0, "reasoning": f"Decision error: {e}"}
    
    def _update_stats(self, coordination: Dict, execution: Dict):
        """Update swarm statistics"""
        try:
            if coordination.get("action") == "execute":
                self.stats["profitable_opportunities"] += 1
                
                if execution.get("processed") and execution.get("action") == "executed":
                    self.stats["executed_trades"] += 1
                    
                    exec_result = execution.get("execution", {})
                    if exec_result.get("success"):
                        profit = exec_result.get("net_profit", 0)
                        self.stats["total_profit"] += profit
                        
        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")
    
    def get_swarm_status(self) -> Dict:
        """Get current swarm status"""
        uptime = time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        
        return {
            "swarm_id": self.swarm_id,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "agents": {
                "solana": self.solana_agent is not None,
                "ethereum": self.ethereum_agent is not None,
                "executor": self.executor is not None
            },
            "price_data": self.price_data_cache,
            "statistics": self.stats.copy(),
            "recent_history": self.arbitrage_history[-5:] if self.arbitrage_history else []
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get detailed performance metrics"""
        if not self.stats["start_time"]:
            return {"error": "Swarm not started"}
        
        uptime_hours = (time.time() - self.stats["start_time"]) / 3600
        
        return {
            "uptime_hours": uptime_hours,
            "total_evaluations": self.stats["total_evaluations"],
            "evaluations_per_hour": self.stats["total_evaluations"] / max(uptime_hours, 0.01),
            "profitable_opportunities": self.stats["profitable_opportunities"],
            "opportunity_rate": self.stats["profitable_opportunities"] / max(self.stats["total_evaluations"], 1),
            "executed_trades": self.stats["executed_trades"],
            "execution_rate": self.stats["executed_trades"] / max(self.stats["profitable_opportunities"], 1),
            "total_profit": self.stats["total_profit"],
            "profit_per_hour": self.stats["total_profit"] / max(uptime_hours, 0.01),
            "executor_stats": self.executor.get_stats() if self.executor else {}
        }
    
    async def stop_swarm(self):
        """Stop the swarm and all agents"""
        logger.info("🛑 Stopping arbitrage swarm...")
        
        self.is_running = False
        
        # Stop all agents
        if self.solana_agent:
            self.solana_agent.stop_monitoring()
        
        if self.ethereum_agent:
            self.ethereum_agent.stop_monitoring()
        
        if self.executor:
            self.executor.stop()
        
        logger.info("✅ Arbitrage swarm stopped")

# Factory function
async def create_arbitrage_swarm(connection: juliaos.JuliaOSConnection) -> ArbitrageSwarmCoordinator:
    """Factory function to create and initialize an arbitrage swarm"""
    swarm = ArbitrageSwarmCoordinator(connection)
    
    success = await swarm.initialize_swarm()
    if not success:
        raise RuntimeError("Failed to initialize arbitrage swarm")
    
    return swarm

# Test function
async def test_swarm_coordination():
    """Test the swarm coordination"""
    from juliaos import JuliaOSConnection
    
    # Create connection
    conn = JuliaOSConnection("http://localhost:8052")
    
    # Create swarm
    swarm = await create_arbitrage_swarm(conn)
    
    # Run for a short time
    coordination_task = asyncio.create_task(swarm.start_coordination())
    
    # Let it run for 30 seconds
    await asyncio.sleep(30)
    
    # Stop and get results
    await swarm.stop_swarm()
    coordination_task.cancel()
    
    # Print results
    status = swarm.get_swarm_status()
    metrics = swarm.get_performance_metrics()
    
    print("Swarm Status:", json.dumps(status, indent=2, default=str))
    print("Performance Metrics:", json.dumps(metrics, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(test_swarm_coordination())
