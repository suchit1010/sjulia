"""
Cross-Chain Arbitrage Dashboard - Flask Web Application
"""
import asyncio
import json
import time
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from threading import Thread
import os
from dotenv import load_dotenv
from loguru import logger

# Import JuliaOS components
import juliaos
from juliaos import JuliaOSConnection

# Import our swarm coordinator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from swarms.arbitrage_coordinator import create_arbitrage_swarm, ArbitrageSwarmCoordinator

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global swarm instance
swarm_coordinator: ArbitrageSwarmCoordinator = None
swarm_task = None

# Configuration
JULIAOS_API_URL = os.getenv("JULIAOS_API_URL", "http://localhost:8052")

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current swarm status"""
    try:
        if swarm_coordinator:
            status = swarm_coordinator.get_swarm_status()
            return jsonify({"success": True, "data": status})
        else:
            return jsonify({"success": False, "error": "Swarm not initialized"})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/metrics')
def get_metrics():
    """Get performance metrics"""
    try:
        if swarm_coordinator:
            metrics = swarm_coordinator.get_performance_metrics()
            return jsonify({"success": True, "data": metrics})
        else:
            return jsonify({"success": False, "error": "Swarm not initialized"})
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/prices')
def get_current_prices():
    """Get current price data from both chains"""
    try:
        if not swarm_coordinator:
            return jsonify({"success": False, "error": "Swarm not initialized"})
        
        prices = {}
        
        if swarm_coordinator.solana_agent:
            prices['solana'] = swarm_coordinator.solana_agent.get_current_price()
        
        if swarm_coordinator.ethereum_agent:
            prices['ethereum'] = swarm_coordinator.ethereum_agent.get_current_price()
        
        # Calculate spread if both prices available
        if 'solana' in prices and 'ethereum' in prices:
            sol_price = prices['solana'].get('price', 0)
            eth_price = prices['ethereum'].get('price', 0)
            
            if sol_price > 0 and eth_price > 0:
                spread = abs(eth_price - sol_price)
                spread_pct = spread / min(sol_price, eth_price)
                
                prices['spread'] = {
                    'absolute': spread,
                    'percentage': spread_pct,
                    'direction': 'eth_higher' if eth_price > sol_price else 'sol_higher'
                }
        
        return jsonify({"success": True, "data": prices})
        
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/history')
def get_trade_history():
    """Get recent arbitrage history"""
    try:
        if not swarm_coordinator:
            return jsonify({"success": False, "error": "Swarm not initialized"})
        
        # Get swarm history
        swarm_history = swarm_coordinator.arbitrage_history[-20:]  # Last 20 entries
        
        # Get executor history
        executor_history = []
        if swarm_coordinator.executor:
            executor_history = swarm_coordinator.executor.get_execution_history(20)
        
        return jsonify({
            "success": True, 
            "data": {
                "swarm_decisions": swarm_history,
                "executions": executor_history
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/start', methods=['POST'])
def start_swarm():
    """Start the arbitrage swarm"""
    global swarm_coordinator, swarm_task
    
    try:
        if swarm_coordinator and swarm_coordinator.is_running:
            return jsonify({"success": False, "error": "Swarm already running"})
        
        # Initialize swarm in a separate thread
        def run_swarm():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def init_and_run():
                global swarm_coordinator
                try:
                    # Create JuliaOS connection
                    conn = JuliaOSConnection(JULIAOS_API_URL)
                    
                    # Create and initialize swarm
                    swarm_coordinator = await create_arbitrage_swarm(conn)
                    
                    # Start coordination
                    await swarm_coordinator.start_coordination()
                    
                except Exception as e:
                    logger.error(f"Error in swarm thread: {e}")
            
            loop.run_until_complete(init_and_run())
        
        swarm_task = Thread(target=run_swarm)
        swarm_task.daemon = True
        swarm_task.start()
        
        # Give it a moment to initialize
        time.sleep(2)
        
        return jsonify({"success": True, "message": "Swarm started successfully"})
        
    except Exception as e:
        logger.error(f"Error starting swarm: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_swarm():
    """Stop the arbitrage swarm"""
    global swarm_coordinator
    
    try:
        if swarm_coordinator:
            # Stop in a separate thread to avoid blocking
            def stop_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(swarm_coordinator.stop_swarm())
            
            stop_thread = Thread(target=stop_async)
            stop_thread.start()
            stop_thread.join(timeout=5)  # Wait max 5 seconds
            
            return jsonify({"success": True, "message": "Swarm stopped successfully"})
        else:
            return jsonify({"success": False, "error": "No swarm to stop"})
            
    except Exception as e:
        logger.error(f"Error stopping swarm: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    try:
        config = {
            "juliaos_api_url": JULIAOS_API_URL,
            "min_profit_threshold": float(os.getenv("MIN_PROFIT_THRESHOLD", "0.02")),
            "max_trade_amount": float(os.getenv("MAX_TRADE_AMOUNT", "100")),
            "slippage_tolerance": float(os.getenv("SLIPPAGE_TOLERANCE", "0.005")),
            "demo_mode": os.getenv("DEMO_MODE", "true").lower() == "true",
            "use_testnet": os.getenv("USE_TESTNET", "true").lower() == "true"
        }
        
        return jsonify({"success": True, "data": config})
        
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/opportunities')
def get_current_opportunities():
    """Get current arbitrage opportunities"""
    try:
        if not swarm_coordinator or not swarm_coordinator.executor:
            return jsonify({"success": False, "error": "Swarm not initialized"})
        
        # Get current prices
        solana_price = swarm_coordinator.solana_agent.get_current_price()
        ethereum_price = swarm_coordinator.ethereum_agent.get_current_price()
        
        # Evaluate opportunity
        opportunity = await_async(
            swarm_coordinator.executor.evaluate_arbitrage_opportunity(
                solana_price, ethereum_price
            )
        )
        
        return jsonify({"success": True, "data": opportunity})
        
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        return jsonify({"success": False, "error": str(e)})

def await_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    logger.info("🚀 Starting Cross-Chain Arbitrage Dashboard...")
    logger.info(f"📡 JuliaOS API URL: {JULIAOS_API_URL}")
    logger.info("🌐 Dashboard will be available at: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )
