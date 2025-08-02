#!/usr/bin/env python3
"""
Complete Cross-Chain Arbitrage System Launcher
Launches the enhanced dashboard with automated trading capabilities
"""
import os
import sys
import asyncio
import threading
import time
from enhanced_dashboard import app
import trading_execution_agent

def print_banner():
    """Print startup banner"""
    banner = """
🚀 CROSS-CHAIN ARBITRAGE TRADING SYSTEM
===============================================
🎯 Features:
  ✅ Real wallet portfolio tracking
  ✅ Automated arbitrage detection  
  ✅ Live trading execution
  ✅ Risk management
  ✅ Multi-chain support (Solana & Ethereum)
  ✅ Professional dashboard UI

⚠️  IMPORTANT:
  • Ensure your .env file is configured
  • Start with small amounts for testing
  • Monitor trades closely
  • This handles REAL funds!

🌐 Dashboard will be available at:
   http://localhost:5000
===============================================
"""
    print(banner)

def check_configuration():
    """Check if the system is properly configured"""
    required_files = ['.env', 'requirements.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check environment variables
    required_env_vars = ['SOLANA_WALLET_ADDRESS', 'ETHEREUM_WALLET_ADDRESS']
    missing_vars = []
    
    with open('.env', 'r') as f:
        env_content = f.read()
        for var in required_env_vars:
            if var not in env_content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please configure your .env file with wallet addresses")
        return False
    
    print("✅ Configuration check passed")
    return True

async def initialize_trading_system():
    """Initialize the trading system"""
    print("🔄 Initializing trading system...")
    
    try:
        # Initialize trading agent
        await trading_execution_agent.initialize_trading_agent()
        print("✅ Trading agent initialized")
        
        print("🎯 Trading System Ready!")
        print("   • Use the dashboard to start/stop automated trading")
        print("   • Monitor your wallet balances in real-time")
        print("   • View arbitrage opportunities and executed trades")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize trading system: {e}")
        return False

def run_dashboard():
    """Run the Flask dashboard"""
    print("🌐 Starting enhanced dashboard...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False for production
        use_reloader=False  # Avoid issues with threading
    )

def main():
    """Main launcher function"""
    print_banner()
    
    # Check configuration
    if not check_configuration():
        print("\n❌ Configuration check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Initialize trading system
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(initialize_trading_system())
        if not success:
            print("❌ Failed to initialize trading system")
            sys.exit(1)
        
        print("\n🚀 Starting dashboard server...")
        print("📊 Open your browser to: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the system")
        
        # Run the dashboard
        run_dashboard()
        
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down trading system...")
        
        # Stop any active trading
        try:
            trading_execution_agent.stop_automated_trading()
            print("✅ Trading stopped")
        except:
            pass
        
        print("👋 Goodbye!")
        
    except Exception as e:
        print(f"\n❌ System error: {e}")
        sys.exit(1)
    
    finally:
        loop.close()

if __name__ == "__main__":
    main()
