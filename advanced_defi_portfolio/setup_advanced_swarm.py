#!/usr/bin/env python3
"""
Advanced Multi-Chain Arbitrage Swarm Setup Script
Automatically installs dependencies and configures the system
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def print_banner():
    print("=" * 80)
    print("🚀 ADVANCED MULTI-CHAIN ARBITRAGE SWARM SETUP")
    print("=" * 80)
    print("Professional DeFi Portfolio Maximization Engine")
    print("✅ Real portfolio analysis")
    print("✅ Cross-chain arbitrage detection") 
    print("✅ Market making opportunities")
    print("✅ Staking optimization")
    print("✅ AI-powered swarm coordination")
    print("=" * 80)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_file = "requirements_advanced.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    print("\n⚙️ Setting up environment configuration...")
    
    env_example = ".env.example"
    env_file = ".env"
    
    if os.path.exists(env_example) and not os.path.exists(env_file):
        shutil.copy(env_example, env_file)
        print(f"✅ Created {env_file} from {env_example}")
        print("📝 Please edit .env file with your API keys and configuration")
    elif os.path.exists(env_file):
        print(f"✅ Environment file {env_file} already exists")
    else:
        print(f"❌ Environment template {env_example} not found")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "logs",
        "data",
        "exports",
        "config",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import aiohttp
        import pandas
        import numpy
        import flask
        import requests
        print("✅ Core dependencies imported successfully")
        
        # Test basic functionality
        print("✅ Installation test passed!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def show_next_steps():
    """Show next steps to user"""
    print("\n🎯 SETUP COMPLETE!")
    print("=" * 80)
    print("Next steps:")
    print("1. Edit .env file with your configuration:")
    print("   - Add your Solana wallet address")
    print("   - Add API keys for enhanced functionality")
    print("   - Configure trading parameters")
    print()
    print("2. Run the advanced arbitrage swarm:")
    print("   python advanced_arbitrage_swarm.py")
    print()
    print("3. Open dashboard in browser:")
    print("   http://localhost:8080")
    print()
    print("🚀 Features available:")
    print("✅ Real-time portfolio analysis")
    print("✅ Cross-chain arbitrage scanning")
    print("✅ Staking yield optimization")
    print("✅ Market making opportunities")
    print("✅ AI-powered recommendations")
    print("✅ Professional web dashboard")
    print("=" * 80)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Test installation
    if not test_installation():
        return False
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
