"""
Arbitrage Executor Agent - Executes arbitrage trades based on swarm decisions
"""
import asyncio
import json
import time
from typing import Dict, Optional, List
from loguru import logger
import os
from dotenv import load_dotenv

# Import JuliaOS components
import juliaos
from juliaos import Agent, AgentBlueprint, AgentState

load_dotenv()

class ArbitrageExecutor:
    """Agent that executes arbitrage trades between Solana and Ethereum"""
    
    def __init__(self, connection: juliaos.JuliaOSConnection):
        self.connection = connection
        self.agent_id = "arbitrage-executor"
        self.agent_name = "Arbitrage Executor"
        self.min_profit_threshold = float(os.getenv("MIN_PROFIT_THRESHOLD", "0.02"))  # 2%
        self.max_trade_amount = float(os.getenv("MAX_TRADE_AMOUNT", "100"))
        self.slippage_tolerance = float(os.getenv("SLIPPAGE_TOLERANCE", "0.005"))  # 0.5%
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        
        self.execution_history = []
        self.is_running = False
        
        # JuliaOS Agent setup
        self.juliaos_agent = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Initialize the JuliaOS agent"""
        try:
            # Create agent blueprint
            blueprint = AgentBlueprint(
                agent_type="ARBITRAGE",
                abilities=["trade_execution", "llm_chat", "risk_assessment"],
                chains=["solana", "ethereum"],
                parameters={
                    "min_profit_threshold": self.min_profit_threshold,
                    "max_trade_amount": self.max_trade_amount,
                    "slippage_tolerance": self.slippage_tolerance,
                    "demo_mode": self.demo_mode
                }
            )
            
            # Create the agent
            self.juliaos_agent = Agent.create(
                self.connection,
                blueprint,
                self.agent_id,
                self.agent_name,
                "Executes arbitrage trades between Solana and Ethereum"
            )
            
            if self.juliaos_agent:
                self.juliaos_agent.set_state(AgentState.RUNNING)
                logger.info(f"✅ Arbitrage Executor created successfully: {self.agent_id}")
            else:
                logger.error("❌ Failed to create Arbitrage Executor")
                
        except Exception as e:
            logger.error(f"❌ Error setting up Arbitrage Executor: {e}")
    
    async def evaluate_arbitrage_opportunity(self, solana_price: Dict, ethereum_price: Dict) -> Dict:
        """Evaluate potential arbitrage opportunity between two prices"""
        try:
            sol_price = solana_price.get("price", 0)
            eth_price = ethereum_price.get("price", 0)
            
            if sol_price <= 0 or eth_price <= 0:
                return {"profitable": False, "reason": "Invalid price data"}
            
            # Calculate price difference and potential profit
            price_diff = abs(eth_price - sol_price)
            price_diff_pct = price_diff / min(sol_price, eth_price)
            
            # Determine direction
            if sol_price < eth_price:
                direction = "sol_to_eth"  # Buy on Solana, sell on Ethereum
                buy_price = sol_price
                sell_price = eth_price
                profit_pct = (sell_price - buy_price) / buy_price
            else:
                direction = "eth_to_sol"  # Buy on Ethereum, sell on Solana
                buy_price = eth_price
                sell_price = sol_price
                profit_pct = (sell_price - buy_price) / buy_price
            
            # Estimate costs (simplified)
            gas_cost_usd = ethereum_price.get("gas_info", {}).get("estimated_cost_eth", 0.004) * 2000  # Assume ETH = $2000
            bridge_fee_pct = 0.001  # 0.1% bridge fee
            slippage_cost_pct = self.slippage_tolerance
            
            # Calculate net profit
            total_cost_pct = bridge_fee_pct + slippage_cost_pct
            net_profit_pct = profit_pct - total_cost_pct
            
            # Check if profitable
            is_profitable = net_profit_pct > self.min_profit_threshold
            
            opportunity = {
                "profitable": is_profitable,
                "direction": direction,
                "buy_chain": "solana" if direction == "sol_to_eth" else "ethereum",
                "sell_chain": "ethereum" if direction == "sol_to_eth" else "solana",
                "buy_price": buy_price,
                "sell_price": sell_price,
                "price_diff": price_diff,
                "price_diff_pct": price_diff_pct,
                "gross_profit_pct": profit_pct,
                "net_profit_pct": net_profit_pct,
                "estimated_costs": {
                    "gas_cost_usd": gas_cost_usd,
                    "bridge_fee_pct": bridge_fee_pct,
                    "slippage_cost_pct": slippage_cost_pct,
                    "total_cost_pct": total_cost_pct
                },
                "recommended_amount": min(self.max_trade_amount, 50) if is_profitable else 0,
                "timestamp": time.time()
            }
            
            if is_profitable:
                logger.info(f"💰 Arbitrage Opportunity: {direction} | Profit: {net_profit_pct:.2%} | Amount: ${opportunity['recommended_amount']}")
            else:
                logger.debug(f"📊 No arbitrage: {direction} | Profit: {net_profit_pct:.2%} (below {self.min_profit_threshold:.2%} threshold)")
            
            return opportunity
            
        except Exception as e:
            logger.error(f"❌ Error evaluating arbitrage: {e}")
            return {"profitable": False, "reason": f"Evaluation error: {e}"}
    
    async def analyze_with_llm(self, opportunity: Dict) -> Dict:
        """Use JuliaOS LLM to analyze arbitrage opportunity"""
        try:
            if not self.juliaos_agent:
                return {"recommendation": "Agent not initialized", "confidence": 0.0}
            
            prompt = f"""
            Analyze this cross-chain arbitrage opportunity:
            
            Direction: {opportunity.get('direction', 'unknown')}
            Buy Price: ${opportunity.get('buy_price', 0):.4f} on {opportunity.get('buy_chain', 'unknown')}
            Sell Price: ${opportunity.get('sell_price', 0):.4f} on {opportunity.get('sell_chain', 'unknown')}
            Net Profit: {opportunity.get('net_profit_pct', 0):.2%}
            Recommended Amount: ${opportunity.get('recommended_amount', 0)}
            
            Costs:
            - Gas: ${opportunity.get('estimated_costs', {}).get('gas_cost_usd', 0):.2f}
            - Bridge Fee: {opportunity.get('estimated_costs', {}).get('bridge_fee_pct', 0):.2%}
            - Slippage: {opportunity.get('estimated_costs', {}).get('slippage_cost_pct', 0):.2%}
            
            Consider:
            1. Market conditions and volatility
            2. Execution risks and timing
            3. Cross-chain bridge reliability
            4. Liquidity on both chains
            
            Provide recommendation: EXECUTE, WAIT, or REJECT with confidence score.
            """
            
            webhook_response = self.juliaos_agent.call_webhook({
                "type": "arbitrage_analysis",
                "prompt": prompt,
                "opportunity": opportunity
            })
            
            if webhook_response:
                return {
                    "recommendation": "EXECUTE" if opportunity.get("profitable", False) else "WAIT",
                    "confidence": 0.85,
                    "reasoning": f"LLM analysis for {opportunity.get('net_profit_pct', 0):.2%} profit opportunity",
                    "raw_response": webhook_response
                }
                
        except Exception as e:
            logger.error(f"❌ LLM analysis error: {e}")
        
        # Fallback analysis
        if opportunity.get("profitable", False) and opportunity.get("net_profit_pct", 0) > self.min_profit_threshold * 2:
            return {
                "recommendation": "EXECUTE",
                "confidence": 0.7,
                "reasoning": f"High profit opportunity: {opportunity.get('net_profit_pct', 0):.2%}"
            }
        else:
            return {
                "recommendation": "WAIT",
                "confidence": 0.6,
                "reasoning": "Insufficient profit or high risk"
            }
    
    async def execute_arbitrage(self, opportunity: Dict, analysis: Dict) -> Dict:
        """Execute the arbitrage trade"""
        try:
            if not opportunity.get("profitable", False):
                return {"success": False, "reason": "Opportunity not profitable"}
            
            if analysis.get("recommendation") != "EXECUTE":
                return {"success": False, "reason": f"LLM recommendation: {analysis.get('recommendation')}"}
            
            trade_amount = opportunity.get("recommended_amount", 0)
            if trade_amount <= 0:
                return {"success": False, "reason": "Invalid trade amount"}
            
            # Simulate trade execution (in demo mode)
            if self.demo_mode:
                return await self._simulate_trade(opportunity, trade_amount)
            else:
                return await self._execute_real_trade(opportunity, trade_amount)
                
        except Exception as e:
            logger.error(f"❌ Error executing arbitrage: {e}")
            return {"success": False, "reason": f"Execution error: {e}"}
    
    async def _simulate_trade(self, opportunity: Dict, amount: float) -> Dict:
        """Simulate trade execution for demo purposes"""
        try:
            trade_id = f"demo-{int(time.time())}"
            direction = opportunity.get("direction", "unknown")
            buy_chain = opportunity.get("buy_chain", "unknown")
            sell_chain = opportunity.get("sell_chain", "unknown")
            
            logger.info(f"🎭 DEMO TRADE: {trade_id}")
            logger.info(f"   Direction: {direction}")
            logger.info(f"   Amount: ${amount}")
            logger.info(f"   Buy on {buy_chain}: ${opportunity.get('buy_price', 0):.4f}")
            logger.info(f"   Sell on {sell_chain}: ${opportunity.get('sell_price', 0):.4f}")
            
            # Simulate execution delay
            await asyncio.sleep(2)
            
            # Calculate simulated profit
            gross_profit = amount * opportunity.get("gross_profit_pct", 0)
            costs = amount * opportunity.get("estimated_costs", {}).get("total_cost_pct", 0)
            net_profit = gross_profit - costs
            
            result = {
                "success": True,
                "trade_id": trade_id,
                "mode": "simulation",
                "direction": direction,
                "amount": amount,
                "buy_chain": buy_chain,
                "sell_chain": sell_chain,
                "buy_price": opportunity.get("buy_price", 0),
                "sell_price": opportunity.get("sell_price", 0),
                "gross_profit": gross_profit,
                "costs": costs,
                "net_profit": net_profit,
                "profit_pct": net_profit / amount,
                "execution_time": 2.0,
                "timestamp": time.time()
            }
            
            # Store in history
            self.execution_history.append(result)
            
            logger.info(f"✅ DEMO TRADE COMPLETED: {trade_id} | Profit: ${net_profit:.2f} ({result['profit_pct']:.2%})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in simulation: {e}")
            return {"success": False, "reason": f"Simulation error: {e}"}
    
    async def _execute_real_trade(self, opportunity: Dict, amount: float) -> Dict:
        """Execute real arbitrage trade (placeholder for production implementation)"""
        # In production, this would:
        # 1. Execute buy transaction on source chain
        # 2. Initiate bridge transfer
        # 3. Execute sell transaction on destination chain
        # 4. Handle any errors or rollbacks
        
        logger.warning("🚨 Real trade execution not implemented - using simulation")
        return await self._simulate_trade(opportunity, amount)
    
    async def process_arbitrage_signal(self, solana_price: Dict, ethereum_price: Dict) -> Dict:
        """Process arbitrage signal from swarm coordinator"""
        try:
            # Evaluate opportunity
            opportunity = await self.evaluate_arbitrage_opportunity(solana_price, ethereum_price)
            
            if not opportunity.get("profitable", False):
                return {
                    "processed": True,
                    "action": "no_action",
                    "reason": opportunity.get("reason", "Not profitable"),
                    "opportunity": opportunity
                }
            
            # Get LLM analysis
            analysis = await self.analyze_with_llm(opportunity)
            
            # Execute if recommended
            if analysis.get("recommendation") == "EXECUTE":
                execution_result = await self.execute_arbitrage(opportunity, analysis)
                
                return {
                    "processed": True,
                    "action": "executed" if execution_result.get("success") else "failed",
                    "opportunity": opportunity,
                    "analysis": analysis,
                    "execution": execution_result
                }
            else:
                return {
                    "processed": True,
                    "action": "deferred",
                    "reason": analysis.get("reasoning", "LLM recommendation"),
                    "opportunity": opportunity,
                    "analysis": analysis
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing arbitrage signal: {e}")
            return {
                "processed": False,
                "action": "error",
                "reason": str(e)
            }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def get_stats(self) -> Dict:
        """Get execution statistics"""
        if not self.execution_history:
            return {
                "total_trades": 0,
                "successful_trades": 0,
                "total_profit": 0.0,
                "avg_profit_pct": 0.0,
                "success_rate": 0.0
            }
        
        successful_trades = [t for t in self.execution_history if t.get("success", False)]
        total_profit = sum(t.get("net_profit", 0) for t in successful_trades)
        total_amount = sum(t.get("amount", 0) for t in successful_trades)
        
        return {
            "total_trades": len(self.execution_history),
            "successful_trades": len(successful_trades),
            "total_profit": total_profit,
            "avg_profit_pct": (total_profit / total_amount) if total_amount > 0 else 0,
            "success_rate": len(successful_trades) / len(self.execution_history)
        }
    
    def stop(self):
        """Stop the executor"""
        self.is_running = False
        if self.juliaos_agent:
            try:
                self.juliaos_agent.set_state(AgentState.STOPPED)
                logger.info("✅ Arbitrage Executor stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping executor: {e}")

# Factory function
async def create_arbitrage_executor(connection: juliaos.JuliaOSConnection) -> ArbitrageExecutor:
    """Factory function to create an arbitrage executor"""
    executor = ArbitrageExecutor(connection)
    return executor

# Test function
async def test_arbitrage_executor():
    """Test the arbitrage executor"""
    from juliaos import JuliaOSConnection
    
    # Create connection
    conn = JuliaOSConnection("http://localhost:8052")
    
    # Create executor
    executor = await create_arbitrage_executor(conn)
    
    # Test with mock price data
    solana_price = {
        "price": 50.0,
        "chain": "solana",
        "exchange": "raydium"
    }
    
    ethereum_price = {
        "price": 52.0,
        "chain": "ethereum",
        "exchange": "uniswap_v3",
        "gas_info": {"estimated_cost_eth": 0.004}
    }
    
    # Test arbitrage evaluation
    opportunity = await executor.evaluate_arbitrage_opportunity(solana_price, ethereum_price)
    print(f"Opportunity: {opportunity}")
    
    # Test LLM analysis
    analysis = await executor.analyze_with_llm(opportunity)
    print(f"Analysis: {analysis}")
    
    # Test execution
    if opportunity.get("profitable"):
        result = await executor.execute_arbitrage(opportunity, analysis)
        print(f"Execution: {result}")
    
    # Get stats
    stats = executor.get_stats()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_arbitrage_executor())
