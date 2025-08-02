#!/usr/bin/env python3
"""
Setup and Run Script for Cross-Chain Arbitrage Trading System
This script handles dependency installation and system startup
"""
import sys
import subprocess
import os
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("🔧 Installing required dependencies...")
    
    dependencies = [
        "cryptography",
        "aiohttp", 
        "flask",
        "flask-cors",
        "requests",
        "pandas",
        "numpy",
        "websockets"
    ]
    
    for dep in dependencies:
        try:
            print(f"📦 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_project_structure():
    """Ensure project structure is correct"""
    print("📁 Setting up project structure...")
    
    required_files = [
        "secure_trading_interface.py",
        "advanced_trading_dashboard.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Create directories for data storage
    os.makedirs("logs", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    print("✅ Project structure verified")
    return True

def run_setup_wizard():
    """Run the interactive setup wizard"""
    print("\n🧙‍♂️ CROSS-CHAIN ARBITRAGE SETUP WIZARD")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        return False
    
    if not setup_project_structure():
        return False
    
    # Install dependencies
    install_deps = input("📦 Install/update dependencies? (yes/no): ").lower()
    if install_deps == "yes":
        if not install_dependencies():
            return False
    
    # Choose what to run
    print("\n🚀 LAUNCH OPTIONS:")
    print("1. 🔐 Secure Trading Interface (Terminal)")
    print("2. 🌐 Advanced Dashboard (Web)")
    print("3. 🎭 Demo Mode Only")
    print("4. 📊 Setup Configuration")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        print("\n🔐 Launching Secure Trading Interface...")
        try:
            import secure_trading_interface
            import asyncio
            asyncio.run(secure_trading_interface.main())
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Make sure all dependencies are installed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "2":
        print("\n🌐 Launching Advanced Dashboard...")
        try:
            import advanced_trading_dashboard
            # This will start the Flask web server
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("Make sure Flask and other web dependencies are installed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "3":
        print("\n🎭 Launching Demo Mode...")
        run_demo_mode()
    
    elif choice == "4":
        print("\n📊 Configuration Setup...")
        setup_configuration()
    
    else:
        print("❌ Invalid choice")
        return False
    
    return True

def run_demo_mode():
    """Run a quick demo of the arbitrage system"""
    print("\n🎭 DEMO MODE - Safe Testing Environment")
    print("=" * 40)
    print("✅ No real funds will be used")
    print("✅ All transactions are simulated")
    print("✅ Perfect for learning and testing")
    
    try:
        import asyncio
        from secure_trading_interface import RealTradingInterface, WalletConfig
        
        # Create demo wallets
        demo_wallets = {
            "solana": WalletConfig("DEMO_SOL_ADDRESS", "solana", "https://api.mainnet-beta.solana.com"),
            "ethereum": WalletConfig("0xDEMO_ETH_ADDRESS", "ethereum", "https://mainnet.infura.io/v3/demo")
        }
        
        # Initialize trading interface in demo mode
        trading_interface = RealTradingInterface(demo_wallets, demo_mode=True)
        
        async def demo_session():
            print("\n📊 Demo Portfolio Status:")
            status = await trading_interface.get_comprehensive_wallet_status()
            
            for chain, wallet_info in status["wallets"].items():
                balance = wallet_info.get("balance", {})
                print(f"✅ {chain.upper()}: {balance.get('balance', 0):.4f} {balance.get('token', 'N/A')}")
            
            print(f"\n💰 Total Portfolio Value: ${status['total_portfolio_value']:.2f}")
            
            # Execute demo trade
            print("\n🚀 Executing demo arbitrage trade...")
            demo_opportunity = {
                "from_chain": "solana",
                "to_chain": "ethereum",
                "amount": 100.0,
                "expected_profit": 25.50,
                "price_difference": 2.5,
                "confidence": 0.85
            }
            
            result = await trading_interface.execute_arbitrage_trade(demo_opportunity)
            
            if result["success"]:
                print(f"✅ Demo trade completed!")
                print(f"💰 Simulated Profit: ${result['profit']:.2f}")
                print(f"🆔 Trade ID: {result['trade_id']}")
            else:
                print(f"❌ Demo trade failed: {result['error']}")
            
            # Show statistics
            stats = await trading_interface.get_trading_statistics()
            print(f"\n📈 Trading Statistics:")
            print(f"   Total Trades: {stats['total_trades']}")
            print(f"   Success Rate: {stats['success_rate']:.1f}%")
            print(f"   Total Profit: ${stats['total_profit']:.2f}")
        
        asyncio.run(demo_session())
        
        print("\n✅ Demo completed successfully!")
        print("💡 Ready to set up real trading? Run this script again and choose option 1")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def setup_configuration():
    """Interactive configuration setup"""
    print("\n📊 CONFIGURATION SETUP")
    print("=" * 30)
    
    config = {}
    
    # Trading limits
    print("💰 Trading Limits:")
    config["max_trade_amount"] = float(input("Max single trade (USD, default 1000): ") or "1000")
    config["max_daily_volume"] = float(input("Max daily volume (USD, default 5000): ") or "5000")
    config["min_profit_threshold"] = float(input("Min profit threshold (USD, default 10): ") or "10")
    
    # Risk settings
    print("\n⚠️ Risk Management:")
    config["max_slippage"] = float(input("Max slippage (%, default 2): ") or "2") / 100
    config["confirmation_required"] = input("Require manual confirmation for real trades? (yes/no): ").lower() == "yes"
    
    # Save configuration
    import json
    with open("config/trading_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved to config/trading_config.json")

if __name__ == "__main__":
    print("🤖 Cross-Chain Arbitrage Trading System")
    print("🔧 Setup and Launch Script")
    print("=" * 50)
    
    try:
        if run_setup_wizard():
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n❌ Setup failed or cancelled")
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your Python installation and try again")
