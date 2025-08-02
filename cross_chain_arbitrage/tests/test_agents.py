"""
Tests for individual agents
"""
import pytest
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.solana_price_agent import SolanaPriceAgent
from agents.ethereum_price_agent import EthereumPriceAgent
from agents.arbitrage_executor import ArbitrageExecutor

# Mock JuliaOS connection for testing
class MockJuliaOSConnection:
    def __init__(self):
        self.api_url = "http://localhost:8052"

class MockJuliaOSAgent:
    def __init__(self, agent_id):
        self.id = agent_id
    
    def set_state(self, state):
        pass
    
    def call_webhook(self, params):
        return {"status": "success", "response": "Mock LLM response"}

# Mock the juliaos module
class MockAgent:
    @classmethod
    def create(cls, conn, blueprint, agent_id, name, description):
        return MockJuliaOSAgent(agent_id)
    
    @classmethod
    def load(cls, conn, agent_id):
        return MockJuliaOSAgent(agent_id)

# Patch the imports
import juliaos
juliaos.Agent = MockAgent

class TestSolanaPriceAgent:
    """Test Solana price monitoring agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a test Solana agent"""
        conn = MockJuliaOSConnection()
        return SolanaPriceAgent(conn)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_id == "solana-price-agent"
        assert agent.agent_name == "Solana Price Monitor"
        assert agent.current_price == 0.0
        assert not agent.is_running
    
    @pytest.mark.asyncio
    async def test_fetch_mock_price(self, agent):
        """Test mock price fetching"""
        price = await agent._get_mock_price("raydium")
        assert isinstance(price, float)
        assert price > 0
    
    @pytest.mark.asyncio
    async def test_llm_analysis(self, agent):
        """Test LLM analysis functionality"""
        price_data = {
            "price": 50.0,
            "exchange": "raydium",
            "timestamp": 1234567890
        }
        
        analysis = await agent.analyze_with_llm(price_data)
        
        assert "analysis" in analysis
        assert "confidence" in analysis
        assert "action" in analysis
        assert isinstance(analysis["confidence"], float)
    
    def test_get_current_price(self, agent):
        """Test getting current price data"""
        agent.current_price = 45.5
        agent.last_update = 1234567890
        
        price_data = agent.get_current_price()
        
        assert price_data["agent_id"] == "solana-price-agent"
        assert price_data["chain"] == "solana"
        assert price_data["exchange"] == "raydium"
        assert price_data["pair"] == "SOL/USDC"
        assert price_data["price"] == 45.5


class TestEthereumPriceAgent:
    """Test Ethereum price monitoring agent"""
    
    @pytest.fixture
    def agent(self):
        """Create a test Ethereum agent"""
        conn = MockJuliaOSConnection()
        return EthereumPriceAgent(conn)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_id == "ethereum-price-agent"
        assert agent.agent_name == "Ethereum Price Monitor"
        assert agent.current_price == 0.0
        assert not agent.is_running
    
    @pytest.mark.asyncio
    async def test_gas_estimation(self, agent):
        """Test gas cost estimation"""
        gas_info = await agent.estimate_gas_costs()
        
        assert "gas_price_gwei" in gas_info
        assert "swap_gas_limit" in gas_info
        assert "estimated_cost_eth" in gas_info
        assert isinstance(gas_info["gas_price_gwei"], float)
    
    @pytest.mark.asyncio
    async def test_fetch_mock_price(self, agent):
        """Test mock price fetching"""
        price = await agent._get_mock_price("uniswap_v3")
        assert isinstance(price, float)
        assert price > 0
    
    def test_get_current_price(self, agent):
        """Test getting current price data"""
        agent.current_price = 52.3
        agent.last_update = 1234567890
        
        price_data = agent.get_current_price()
        
        assert price_data["agent_id"] == "ethereum-price-agent"
        assert price_data["chain"] == "ethereum"
        assert price_data["exchange"] == "uniswap_v3"
        assert price_data["pair"] == "wSOL/USDC"
        assert price_data["price"] == 52.3


class TestArbitrageExecutor:
    """Test arbitrage execution agent"""
    
    @pytest.fixture
    def executor(self):
        """Create a test arbitrage executor"""
        conn = MockJuliaOSConnection()
        return ArbitrageExecutor(conn)
    
    def test_executor_initialization(self, executor):
        """Test executor initializes correctly"""
        assert executor.agent_id == "arbitrage-executor"
        assert executor.agent_name == "Arbitrage Executor"
        assert executor.min_profit_threshold == 0.02  # 2%
        assert executor.demo_mode == True
        assert len(executor.execution_history) == 0
    
    @pytest.mark.asyncio
    async def test_evaluate_arbitrage_opportunity(self, executor):
        """Test arbitrage opportunity evaluation"""
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
        
        opportunity = await executor.evaluate_arbitrage_opportunity(
            solana_price, ethereum_price
        )
        
        assert "profitable" in opportunity
        assert "direction" in opportunity
        assert "buy_price" in opportunity
        assert "sell_price" in opportunity
        assert "net_profit_pct" in opportunity
        assert isinstance(opportunity["profitable"], bool)
    
    @pytest.mark.asyncio
    async def test_simulate_trade(self, executor):
        """Test trade simulation"""
        opportunity = {
            "profitable": True,
            "direction": "sol_to_eth",
            "buy_chain": "solana",
            "sell_chain": "ethereum",
            "buy_price": 50.0,
            "sell_price": 52.0,
            "gross_profit_pct": 0.04,
            "estimated_costs": {"total_cost_pct": 0.01}
        }
        
        result = await executor._simulate_trade(opportunity, 100.0)
        
        assert result["success"] == True
        assert result["mode"] == "simulation"
        assert "trade_id" in result
        assert "net_profit" in result
        assert isinstance(result["net_profit"], float)
    
    def test_get_stats(self, executor):
        """Test statistics calculation"""
        # Add some mock execution history
        executor.execution_history = [
            {"success": True, "net_profit": 2.0, "amount": 100.0},
            {"success": True, "net_profit": 1.5, "amount": 50.0},
            {"success": False, "net_profit": 0.0, "amount": 75.0}
        ]
        
        stats = executor.get_stats()
        
        assert stats["total_trades"] == 3
        assert stats["successful_trades"] == 2
        assert stats["total_profit"] == 3.5
        assert stats["success_rate"] == 2/3


# Integration test
class TestAgentIntegration:
    """Test integration between agents"""
    
    @pytest.mark.asyncio
    async def test_full_arbitrage_flow(self):
        """Test complete arbitrage evaluation flow"""
        conn = MockJuliaOSConnection()
        
        # Create agents
        solana_agent = SolanaPriceAgent(conn)
        ethereum_agent = EthereumPriceAgent(conn)
        executor = ArbitrageExecutor(conn)
        
        # Mock price data
        solana_agent.current_price = 50.0
        solana_agent.last_update = 1234567890
        
        ethereum_agent.current_price = 52.0
        ethereum_agent.last_update = 1234567890
        
        # Get price data
        sol_price = solana_agent.get_current_price()
        eth_price = ethereum_agent.get_current_price()
        
        # Evaluate opportunity
        opportunity = await executor.evaluate_arbitrage_opportunity(sol_price, eth_price)
        
        # Check if profitable
        if opportunity["profitable"]:
            # Get LLM analysis
            analysis = await executor.analyze_with_llm(opportunity)
            
            # Execute if recommended
            if analysis["recommendation"] == "EXECUTE":
                result = await executor.execute_arbitrage(opportunity, analysis)
                assert result["success"] == True
        
        # Verify the flow completed without errors
        assert opportunity is not None
        assert "profitable" in opportunity


if __name__ == "__main__":
    pytest.main([__file__])
