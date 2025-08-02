"""
Simple test runner to validate the core functionality
"""
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from loguru import logger

# Mock JuliaOS for testing
class MockJuliaOSConnection:
    def __init__(self):
        self.api_url = "http://localhost:8052"

class MockAgent:
    @classmethod
    def create(cls, conn, blueprint, agent_id, name, description):
        return cls(agent_id)
    
    def __init__(self, agent_id):
        self.id = agent_id
    
    def set_state(self, state):
        pass
    
    def call_webhook(self, params):
        return {"status": "success", "response": "Mock LLM response"}

# Create mock juliaos module
import types
juliaos = types.ModuleType('juliaos')
juliaos.JuliaOSConnection = MockJuliaOSConnection
juliaos.Agent = MockAgent

class MockAgentBlueprint:
    def __init__(self, **kwargs):
        pass

class MockAgentState:
    RUNNING = "running"
    STOPPED = "stopped"

juliaos.AgentBlueprint = MockAgentBlueprint
juliaos.AgentState = MockAgentState

# Add to sys.modules
sys.modules['juliaos'] = juliaos

async def test_price_agents():
    """Test price monitoring agents"""
    logger.info("🧪 Testing price monitoring agents...")
    
    try:
        from agents.solana_price_agent import SolanaPriceAgent
        from agents.ethereum_price_agent import EthereumPriceAgent
        
        conn = MockJuliaOSConnection()
        
        # Test Solana agent
        solana_agent = SolanaPriceAgent(conn)
        sol_price = await solana_agent._get_mock_price("raydium")
        logger.info(f"✅ Solana agent mock price: ${sol_price:.2f}")
        
        # Test Ethereum agent
        ethereum_agent = EthereumPriceAgent(conn)
        eth_price = await ethereum_agent._get_mock_price("uniswap_v3")
        logger.info(f"✅ Ethereum agent mock price: ${eth_price:.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Price agent test failed: {e}")
        return False

async def test_arbitrage_executor():
    """Test arbitrage execution"""
    logger.info("🧪 Testing arbitrage executor...")
    
    try:
        from agents.arbitrage_executor import ArbitrageExecutor
        
        conn = MockJuliaOSConnection()
        executor = ArbitrageExecutor(conn)
        
        # Test opportunity evaluation
        solana_price = {"price": 50.0, "chain": "solana", "exchange": "raydium"}
        ethereum_price = {"price": 52.0, "chain": "ethereum", "exchange": "uniswap_v3", "gas_info": {"estimated_cost_eth": 0.004}}
        
        opportunity = await executor.evaluate_arbitrage_opportunity(solana_price, ethereum_price)
        logger.info(f"✅ Arbitrage opportunity: {opportunity['profitable']} | Profit: {opportunity['net_profit_pct']:.2%}")
        
        # Test execution if profitable
        if opportunity['profitable']:
            analysis = await executor.analyze_with_llm(opportunity)
            result = await executor.execute_arbitrage(opportunity, analysis)
            logger.info(f"✅ Trade execution: {result['success']} | Profit: ${result.get('net_profit', 0):.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Arbitrage executor test failed: {e}")
        return False

async def test_swarm_coordinator():
    """Test swarm coordination"""
    logger.info("🧪 Testing swarm coordinator...")
    
    try:
        from swarms.arbitrage_coordinator import ArbitrageSwarmCoordinator
        
        conn = MockJuliaOSConnection()
        coordinator = ArbitrageSwarmCoordinator(conn)
        
        # Initialize swarm
        await coordinator.initialize_swarm()
        logger.info("✅ Swarm coordinator initialized")
        
        # Test one coordination cycle
        await coordinator._coordination_cycle()
        logger.info("✅ Coordination cycle completed")
        
        # Get status
        status = coordinator.get_swarm_status()
        logger.info(f"✅ Swarm status: {status['swarm_id']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Swarm coordinator test failed: {e}")
        return False

async def test_web_interface():
    """Test web interface"""
    logger.info("🧪 Testing web interface...")
    
    try:
        from ui.app import create_app
        
        app = create_app()
        logger.info("✅ Flask app created successfully")
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            logger.info(f"✅ Dashboard page: {response.status_code}")
            
            # Test API endpoints
            response = client.get('/api/config')
            logger.info(f"✅ Config API: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Web interface test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting Cross-Chain Arbitrage Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Price Agents", test_price_agents),
        ("Arbitrage Executor", test_arbitrage_executor),
        ("Swarm Coordinator", test_swarm_coordinator),
        ("Web Interface", test_web_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n📊 Test Results Summary:")
    logger.info("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The system is ready to run.")
        return True
    else:
        logger.warning("⚠️ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    # Run tests
    success = asyncio.run(run_all_tests())
    
    if success:
        logger.info("\n🚀 Ready to run the full demo with:")
        logger.info("   python scripts/run_demo.py")
    else:
        logger.error("\n❌ Please fix the issues before running the demo")
    
    sys.exit(0 if success else 1)
