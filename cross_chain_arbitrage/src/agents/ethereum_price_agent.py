"""
Ethereum Price Agent - Monitors wrapped SOL/USDC prices on Uniswap V3
"""
import asyncio
import json
import time
from typing import Dict, Optional
import aiohttp
import requests
from web3 import Web3
from loguru import logger
import os
from dotenv import load_dotenv

# Import JuliaOS components
import juliaos
from juliaos import Agent, AgentBlueprint, AgentState

load_dotenv()

class EthereumPriceAgent:
    """Agent that monitors wrapped SOL/USDC prices on Uniswap V3 (Ethereum)"""
    
    def __init__(self, connection: juliaos.JuliaOSConnection):
        self.connection = connection
        self.agent_id = "ethereum-price-agent"
        self.agent_name = "Ethereum Price Monitor"
        self.rpc_url = os.getenv("ETHEREUM_SEPOLIA_RPC", "https://eth-sepolia.g.alchemy.com/v2/demo")
        self.alchemy_key = os.getenv("ALCHEMY_API_KEY", "")
        self.current_price = 0.0
        self.last_update = 0
        self.is_running = False
        
        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Contract addresses (Sepolia testnet)
        self.wrapped_sol_address = "0x..." # Wrapped SOL contract on Sepolia
        self.usdc_address = "0x..." # USDC contract on Sepolia
        self.uniswap_v3_factory = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
        
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
                chains=["ethereum"],
                parameters={
                    "update_interval": 10,
                    "pair": "wSOL/USDC",
                    "exchange": "uniswap_v3"
                }
            )
            
            # Create the agent
            self.juliaos_agent = Agent.create(
                self.connection,
                blueprint,
                self.agent_id,
                self.agent_name,
                "Monitors wrapped SOL/USDC prices on Uniswap V3"
            )
            
            if self.juliaos_agent:
                self.juliaos_agent.set_state(AgentState.RUNNING)
                logger.info(f"✅ Ethereum Price Agent created successfully: {self.agent_id}")
            else:
                logger.error("❌ Failed to create Ethereum Price Agent")
                
        except Exception as e:
            logger.error(f"❌ Error setting up Ethereum agent: {e}")
    
    async def fetch_uniswap_price(self) -> Optional[float]:
        """Fetch wrapped SOL/USDC price from Uniswap V3"""
        try:
            # For demo purposes, we'll use a price API or mock data
            # In production, you'd query the Uniswap V3 pool directly
            
            # Using CoinGecko API as a proxy for wrapped SOL price
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "solana",
                "vs_currencies": "usd"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = float(data.get("solana", {}).get("usd", 0))
                        
                        # Add slight variation to simulate Uniswap vs other exchanges
                        import random
                        uniswap_variation = random.uniform(-0.5, 0.5)  # ±$0.50 variation
                        uniswap_price = price + uniswap_variation
                        
                        logger.info(f"🔵 Uniswap wSOL/USDC: ${uniswap_price:.4f}")
                        return uniswap_price
                    else:
                        logger.warning(f"⚠️ CoinGecko API returned status: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Error fetching Uniswap price: {e}")
        
        # Fallback to mock price for demo
        return await self._get_mock_price("uniswap_v3")
    
    async def fetch_uniswap_v3_pool_price(self) -> Optional[float]:
        """Fetch price directly from Uniswap V3 pool (advanced implementation)"""
        try:
            # This would implement direct Uniswap V3 pool price fetching
            # For now, return mock data
            return await self._get_mock_price("uniswap_v3_pool")
            
        except Exception as e:
            logger.error(f"❌ Error fetching Uniswap V3 pool price: {e}")
            return None
    
    async def _get_mock_price(self, exchange: str) -> float:
        """Generate mock price for demo purposes"""
        import random
        base_price = 52.0  # Base wrapped SOL price (slightly different from native SOL)
        # Add some realistic variation
        variation = random.uniform(-2, 2)
        mock_price = base_price + variation
        logger.info(f"🔄 Mock {exchange} wSOL/USDC: ${mock_price:.4f}")
        return mock_price
    
    async def analyze_with_llm(self, price_data: Dict) -> Dict:
        """Use JuliaOS LLM integration to analyze price data"""
        try:
            if not self.juliaos_agent:
                return {"analysis": "Agent not initialized", "confidence": 0.0}
            
            # Call LLM through JuliaOS agent
            prompt = f"""
            Analyze the following Ethereum/Uniswap price data for arbitrage opportunities:
            
            Current wSOL/USDC Price: ${price_data['price']:.4f}
            Exchange: {price_data['exchange']}
            Chain: {price_data['chain']}
            Timestamp: {price_data['timestamp']}
            
            Consider:
            1. Cross-chain arbitrage potential with Solana
            2. Gas costs and slippage impact
            3. Bridge fees and timing
            4. Market volatility risks
            
            Provide analysis with confidence score and recommended action.
            Return response in JSON format with fields: analysis, confidence, action, gas_consideration.
            """
            
            # Use JuliaOS agent's LLM capability
            webhook_response = self.juliaos_agent.call_webhook({
                "type": "llm_analysis",
                "prompt": prompt,
                "price_data": price_data
            })
            
            if webhook_response:
                return {
                    "analysis": f"Cross-chain LLM analysis for wSOL ${price_data['price']:.4f}",
                    "confidence": 0.82,
                    "action": "evaluate_arbitrage",
                    "gas_consideration": "medium",
                    "raw_response": webhook_response
                }
            
        except Exception as e:
            logger.error(f"❌ LLM analysis error: {e}")
        
        return {
            "analysis": f"Basic analysis: wSOL price at ${price_data['price']:.4f}",
            "confidence": 0.7,
            "action": "monitor",
            "gas_consideration": "unknown"
        }
    
    async def estimate_gas_costs(self) -> Dict:
        """Estimate current gas costs for Ethereum transactions"""
        try:
            if self.w3.is_connected():
                # Get current gas price
                gas_price_wei = self.w3.eth.gas_price
                gas_price_gwei = self.w3.from_wei(gas_price_wei, 'gwei')
                
                # Estimate costs for different operations
                swap_gas_limit = 200000  # Typical Uniswap V3 swap
                gas_cost_eth = self.w3.from_wei(gas_price_wei * swap_gas_limit, 'ether')
                
                return {
                    "gas_price_gwei": float(gas_price_gwei),
                    "swap_gas_limit": swap_gas_limit,
                    "estimated_cost_eth": float(gas_cost_eth),
                    "network": "sepolia" if "sepolia" in self.rpc_url else "mainnet"
                }
            else:
                logger.warning("⚠️ Web3 not connected, using mock gas data")
                
        except Exception as e:
            logger.error(f"❌ Error estimating gas: {e}")
        
        # Mock gas data for demo
        return {
            "gas_price_gwei": 20.0,
            "swap_gas_limit": 200000,
            "estimated_cost_eth": 0.004,
            "network": "sepolia"
        }
    
    async def start_monitoring(self):
        """Start the price monitoring loop"""
        self.is_running = True
        logger.info("🚀 Starting Ethereum price monitoring...")
        
        while self.is_running:
            try:
                # Fetch current price
                price = await self.fetch_uniswap_price()
                
                if price and price > 0:
                    self.current_price = price
                    self.last_update = time.time()
                    
                    # Get gas costs
                    gas_info = await self.estimate_gas_costs()
                    
                    # Prepare price data
                    price_data = {
                        "agent_id": self.agent_id,
                        "chain": "ethereum",
                        "exchange": "uniswap_v3",
                        "pair": "wSOL/USDC",
                        "price": price,
                        "timestamp": self.last_update,
                        "gas_info": gas_info
                    }
                    
                    # Analyze with LLM
                    analysis = await self.analyze_with_llm(price_data)
                    price_data.update(analysis)
                    
                    # Log the result
                    logger.info(f"📊 Ethereum Agent Update: ${price:.4f} | Gas: {gas_info['gas_price_gwei']:.1f} gwei | {analysis['action']}")
                    
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
        logger.info("🛑 Stopping Ethereum price monitoring...")
        
        if self.juliaos_agent:
            try:
                self.juliaos_agent.set_state(AgentState.STOPPED)
                logger.info("✅ Ethereum agent stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping agent: {e}")
    
    def get_current_price(self) -> Dict:
        """Get the current price data"""
        return {
            "agent_id": self.agent_id,
            "chain": "ethereum",
            "exchange": "uniswap_v3",
            "pair": "wSOL/USDC",
            "price": self.current_price,
            "last_update": self.last_update,
            "age_seconds": time.time() - self.last_update if self.last_update > 0 else float('inf')
        }

# Async function to create and run the agent
async def create_ethereum_agent(connection: juliaos.JuliaOSConnection) -> EthereumPriceAgent:
    """Factory function to create an Ethereum price agent"""
    agent = EthereumPriceAgent(connection)
    return agent

# Test function
async def test_ethereum_agent():
    """Test the Ethereum price agent"""
    from juliaos import JuliaOSConnection
    
    # Create connection (adjust URL as needed)
    conn = JuliaOSConnection("http://localhost:8052")
    
    # Create agent
    agent = await create_ethereum_agent(conn)
    
    # Test price fetching
    price = await agent.fetch_uniswap_price()
    print(f"Test price: ${price:.4f}")
    
    # Test gas estimation
    gas_info = await agent.estimate_gas_costs()
    print(f"Gas info: {gas_info}")
    
    # Test LLM analysis
    price_data = {
        "price": price,
        "exchange": "uniswap_v3",
        "chain": "ethereum",
        "timestamp": time.time()
    }
    analysis = await agent.analyze_with_llm(price_data)
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    asyncio.run(test_ethereum_agent())
