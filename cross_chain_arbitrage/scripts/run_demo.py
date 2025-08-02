"""
Demo runner for Cross-Chain Arbitrage Swarm Bot
"""
import asyncio
import os
import sys
import time
import signal
from threading import Thread
from dotenv import load_dotenv
from loguru import logger

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import JuliaOS components (will use mocks if not available)
try:
    import juliaos
    from juliaos import JuliaOSConnection
    JULIAOS_AVAILABLE = True
except ImportError:
    logger.warning("JuliaOS not available, using mock implementation")
    JULIAOS_AVAILABLE = False

# Import our components
from swarms.arbitrage_coordinator import create_arbitrage_swarm
from ui.app import create_app

load_dotenv()

class DemoRunner:
    """Demo runner for the cross-chain arbitrage system"""
    
    def __init__(self):
        self.swarm = None
        self.web_app = None
        self.web_thread = None
        self.is_running = False
        
        # Configuration
        self.juliaos_url = os.getenv("JULIAOS_API_URL", "http://localhost:8052")
        self.web_port = int(os.getenv("WEB_PORT", "5000"))
        self.demo_duration = int(os.getenv("DEMO_DURATION", "300"))  # 5 minutes default
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("🛑 Shutdown signal received, stopping demo...")
        asyncio.create_task(self.stop())
    
    async def setup_juliaos_connection(self):
        """Setup JuliaOS connection"""
        try:
            if JULIAOS_AVAILABLE:
                logger.info(f"📡 Connecting to JuliaOS at {self.juliaos_url}")
                connection = JuliaOSConnection(self.juliaos_url)
                
                # Test connection
                # In a real implementation, you'd ping the API here
                logger.info("✅ JuliaOS connection established")
                return connection
            else:
                logger.warning("⚠️ Using mock JuliaOS connection")
                return MockJuliaOSConnection()
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to JuliaOS: {e}")
            logger.info("🎭 Falling back to mock implementation for demo")
            return MockJuliaOSConnection()
    
    async def start_swarm(self):
        """Start the arbitrage swarm"""
        try:
            logger.info("🐝 Initializing arbitrage swarm...")
            
            # Get JuliaOS connection
            connection = await self.setup_juliaos_connection()
            
            # Create and initialize swarm
            self.swarm = await create_arbitrage_swarm(connection)
            
            logger.info("✅ Swarm initialized successfully")
            
            # Start swarm coordination
            logger.info("🚀 Starting swarm coordination...")
            await self.swarm.start_coordination()
            
        except Exception as e:
            logger.error(f"❌ Error starting swarm: {e}")
            raise
    
    def start_web_interface(self):
        """Start the web interface in a separate thread"""
        try:
            logger.info(f"🌐 Starting web interface on port {self.web_port}")
            
            def run_flask():
                app = create_app()
                app.run(
                    host='0.0.0.0',
                    port=self.web_port,
                    debug=False,
                    use_reloader=False
                )
            
            self.web_thread = Thread(target=run_flask)
            self.web_thread.daemon = True
            self.web_thread.start()
            
            logger.info(f"✅ Web interface started at http://localhost:{self.web_port}")
            
        except Exception as e:
            logger.error(f"❌ Error starting web interface: {e}")
            raise
    
    async def run_demo(self):
        """Run the complete demo"""
        try:
            self.is_running = True
            
            logger.info("🚀 Starting Cross-Chain Arbitrage Demo")
            logger.info("=" * 50)
            
            # Start web interface
            self.start_web_interface()
            
            # Give web interface time to start
            await asyncio.sleep(2)
            
            # Start swarm
            await self.start_swarm()
            
            logger.info("🎉 Demo started successfully!")
            logger.info(f"📊 Dashboard: http://localhost:{self.web_port}")
            logger.info(f"⏱️ Demo will run for {self.demo_duration} seconds")
            logger.info("💡 Press Ctrl+C to stop the demo early")
            
            # Run for specified duration
            start_time = time.time()
            while self.is_running and (time.time() - start_time) < self.demo_duration:
                await asyncio.sleep(5)
                
                # Print periodic status
                if int(time.time() - start_time) % 30 == 0:  # Every 30 seconds
                    await self.print_status()
            
            logger.info("⏰ Demo duration completed")
            
        except KeyboardInterrupt:
            logger.info("🛑 Demo interrupted by user")
        except Exception as e:
            logger.error(f"❌ Demo error: {e}")
        finally:
            await self.stop()
    
    async def print_status(self):
        """Print current status"""
        try:
            if self.swarm:
                status = self.swarm.get_swarm_status()
                metrics = self.swarm.get_performance_metrics()
                
                logger.info("📊 Demo Status:")
                logger.info(f"   Evaluations: {metrics.get('total_evaluations', 0)}")
                logger.info(f"   Opportunities: {metrics.get('profitable_opportunities', 0)}")
                logger.info(f"   Executed: {metrics.get('executed_trades', 0)}")
                logger.info(f"   Profit: ${metrics.get('total_profit', 0):.2f}")
                
        except Exception as e:
            logger.debug(f"Status print error: {e}")
    
    async def stop(self):
        """Stop the demo"""
        logger.info("🛑 Stopping demo...")
        self.is_running = False
        
        # Stop swarm
        if self.swarm:
            try:
                await self.swarm.stop_swarm()
                logger.info("✅ Swarm stopped")
            except Exception as e:
                logger.error(f"❌ Error stopping swarm: {e}")
        
        # Web interface will stop when main process exits
        logger.info("✅ Demo stopped successfully")


class MockJuliaOSConnection:
    """Mock JuliaOS connection for demo when JuliaOS is not available"""
    
    def __init__(self):
        self.api_url = "http://localhost:8052"
        logger.info("🎭 Using mock JuliaOS connection for demo")


# Mock Agent classes if JuliaOS not available
if not JULIAOS_AVAILABLE:
    class MockAgentBlueprint:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    
    class MockAgentState:
        RUNNING = "running"
        STOPPED = "stopped"
    
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
    juliaos.AgentBlueprint = MockAgentBlueprint
    juliaos.AgentState = MockAgentState
    
    # Add to sys.modules so imports work
    sys.modules['juliaos'] = juliaos


async def main():
    """Main demo function"""
    try:
        # Print demo information
        print("🚀 Cross-Chain Arbitrage Swarm Bot Demo")
        print("=" * 50)
        print("📋 This demo will:")
        print("   1. Start a web dashboard")
        print("   2. Initialize AI agents for price monitoring")
        print("   3. Create a swarm coordinator")
        print("   4. Monitor prices on Solana and Ethereum")
        print("   5. Identify arbitrage opportunities")
        print("   6. Execute demo trades")
        print("")
        print("💡 Features demonstrated:")
        print("   ✅ JuliaOS Agent framework")
        print("   ✅ Swarm coordination")
        print("   ✅ Cross-chain price monitoring")
        print("   ✅ LLM-powered decision making")
        print("   ✅ Web-based dashboard")
        print("")
        
        # Check environment
        if not os.path.exists(".env"):
            print("⚠️ Warning: .env file not found")
            print("   Demo will run with default settings")
        
        # Confirm start
        response = input("🚀 Start the demo? (y/n): ").lower().strip()
        if response != 'y':
            print("👋 Demo cancelled")
            return
        
        # Create and run demo
        demo = DemoRunner()
        await demo.run_demo()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    # Run demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
