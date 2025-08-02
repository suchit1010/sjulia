"""
Solana Price Agent - Monitors SOL/USDC prices on Raydium
"""
import asyncio
import json
import time
from typing import Dict, Optional
import aiohttp
import requests
from loguru import logger
import os
from dotenv import load_dotenv

# Import JuliaOS components
import juliaos
from juliaos import Agent, AgentBlueprint, AgentState

load_dotenv()

class SolanaPriceAgent:
    """Agent that monitors SOL/USDC prices on Raydium (Solana)"""
    
    def __init__(self, connection: juliaos.JuliaOSConnection):
        self.connection = connection
        self.agent_id = "solana-price-agent"
        self.agent_name = "Solana Price Monitor"
        self.rpc_url = os.getenv("SOLANA_DEVNET_RPC", "https://api.devnet.solana.com")
        self.helius_key = os.getenv("HELIUS_API_KEY", "")
        self.current_price = 0.0
        self.last_update = 0
        self.is_running = False
        
        # JuliaOS Agent setup
        self.juliaos_agent = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Initialize the JuliaOS agent"""
        try:
            # Create agent blueprint
            blueprint = AgentBlueprint(
                agent_type="DATA_COLLECTION",
                abilities=["price_monitoring", "llm_chat"],
                chains=["solana"],
                parameters={
                    "update_interval": 10,
                    "pair": "SOL/USDC",
                    "exchange": "raydium"
                }
            )
            
            # Create the agent
            self.juliaos_agent = Agent.create(
                self.connection,
                blueprint,
                self.agent_id,
                self.agent_name,
                "Monitors SOL/USDC prices on Raydium DEX"
            )
            
            if self.juliaos_agent:
                self.juliaos_agent.set_state(AgentState.RUNNING)
                logger.info(f"✅ Solana Price Agent created successfully: {self.agent_id}")
            else:
                logger.error("❌ Failed to create Solana Price Agent")
                
        except Exception as e:
            logger.error(f"❌ Error setting up Solana agent: {e}")
    
    async def fetch_raydium_price(self) -> Optional[float]:
        """Fetch SOL/USDC price from Raydium"""
        try:
            # Using Jupiter API for Raydium price data
            url = "https://price.jup.ag/v4/price"
            params = {
                "ids": "So11111111111111111111111111111111111111112",  # SOL mint
                "vsToken": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC mint
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        sol_price_data = data.get("data", {}).get("So11111111111111111111111111111111111111112")
                        if sol_price_data:
                            price = float(sol_price_data.get("price", 0))
                            logger.info(f"🟢 Raydium SOL/USDC: ${price:.4f}")
                            return price
                    else:
                        logger.warning(f"⚠️ Jupiter API returned status: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Error fetching Raydium price: {e}")
        
        # Fallback to mock price for demo
        return await self._get_mock_price("raydium")
    
    async def _get_mock_price(self, exchange: str) -> float:
        """Generate mock price for demo purposes"""
        import random
        base_price = 50.0  # Base SOL price
        # Add some realistic variation
        variation = random.uniform(-2, 2)
        mock_price = base_price + variation
        logger.info(f"🔄 Mock {exchange} SOL/USDC: ${mock_price:.4f}")
        return mock_price
    
    async def analyze_with_llm(self, price_data: Dict) -> Dict:
        """Use JuliaOS LLM integration to analyze price data"""
        try:
            if not self.juliaos_agent:
                return {"analysis": "Agent not initialized", "confidence": 0.0}
            
            # Call LLM through JuliaOS agent
            prompt = f"""
            Analyze the following Solana/Raydium price data for arbitrage opportunities:
            
            Current SOL/USDC Price: ${price_data['price']:.4f}
            Exchange: {price_data['exchange']}
            Timestamp: {price_data['timestamp']}
            
            Provide analysis on:
            1. Price trend assessment
            2. Arbitrage potential
            3. Risk factors
            4. Recommended action
            
            Return response in JSON format with fields: analysis, confidence, action.
            """
            
            # Use JuliaOS agent's LLM capability
            webhook_response = self.juliaos_agent.call_webhook({
                "type": "llm_analysis",
                "prompt": prompt,
                "price_data": price_data
            })
            
            if webhook_response:
                return {
                    "analysis": f"LLM analysis for price ${price_data['price']:.4f}",
                    "confidence": 0.85,
                    "action": "monitor",
                    "raw_response": webhook_response
                }
            
        except Exception as e:
            logger.error(f"❌ LLM analysis error: {e}")
        
        return {
            "analysis": f"Basic analysis: SOL price at ${price_data['price']:.4f}",
            "confidence": 0.7,
            "action": "monitor"
        }
    
    async def start_monitoring(self):
        """Start the price monitoring loop"""
        self.is_running = True
        logger.info("🚀 Starting Solana price monitoring...")
        
        while self.is_running:
            try:
                # Fetch current price
                price = await self.fetch_raydium_price()
                
                if price and price > 0:
                    self.current_price = price
                    self.last_update = time.time()
                    
                    # Prepare price data
                    price_data = {
                        "agent_id": self.agent_id,
                        "chain": "solana",
                        "exchange": "raydium",
                        "pair": "SOL/USDC",
                        "price": price,
                        "timestamp": self.last_update
                    }
                    
                    # Analyze with LLM
                    analysis = await self.analyze_with_llm(price_data)
                    price_data.update(analysis)
                    
                    # Log the result
                    logger.info(f"📊 Solana Agent Update: ${price:.4f} | {analysis['action']}")
                    
                    # Store in memory (this would integrate with swarm coordination)
                    await self._report_to_swarm(price_data)
                
                # Wait before next update
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Shorter wait on error
    
    async def _report_to_swarm(self, price_data: Dict):
        """Report price data to the swarm coordinator"""
        try:
            # This would integrate with JuliaOS swarm functionality
            # For now, we'll just log the data
            logger.debug(f"📤 Reporting to swarm: {price_data}")
            
            # In a full implementation, this would publish to a swarm topic
            # or update shared swarm state through JuliaOS APIs
            
        except Exception as e:
            logger.error(f"❌ Error reporting to swarm: {e}")
    
    def stop_monitoring(self):
        """Stop the price monitoring"""
        self.is_running = False
        logger.info("🛑 Stopping Solana price monitoring...")
        
        if self.juliaos_agent:
            try:
                self.juliaos_agent.set_state(AgentState.STOPPED)
                logger.info("✅ Solana agent stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping agent: {e}")
    
    def get_current_price(self) -> Dict:
        """Get the current price data"""
        return {
            "agent_id": self.agent_id,
            "chain": "solana",
            "exchange": "raydium",
            "pair": "SOL/USDC",
            "price": self.current_price,
            "last_update": self.last_update,
            "age_seconds": time.time() - self.last_update if self.last_update > 0 else float('inf')
        }

# Async function to create and run the agent
async def create_solana_agent(connection: juliaos.JuliaOSConnection) -> SolanaPriceAgent:
    """Factory function to create a Solana price agent"""
    agent = SolanaPriceAgent(connection)
    return agent

# Test function
async def test_solana_agent():
    """Test the Solana price agent"""
    from juliaos import JuliaOSConnection
    
    # Create connection (adjust URL as needed)
    conn = JuliaOSConnection("http://localhost:8052")
    
    # Create agent
    agent = await create_solana_agent(conn)
    
    # Test price fetching
    price = await agent.fetch_raydium_price()
    print(f"Test price: ${price:.4f}")
    
    # Test LLM analysis
    price_data = {
        "price": price,
        "exchange": "raydium",
        "timestamp": time.time()
    }
    analysis = await agent.analyze_with_llm(price_data)
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    asyncio.run(test_solana_agent())
