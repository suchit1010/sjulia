#!/usr/bin/env python3
"""
Quick Setup for Advanced Multi-Chain Arbitrage Swarm
Installs only essential dependencies to avoid conflicts
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def print_banner():
    print("=" * 80)
    print("🚀 QUICK SETUP - ADVANCED ARBITRAGE SWARM")
    print("=" * 80)
    print("Installing essential dependencies only...")
    print("=" * 80)

def install_core_dependencies():
    """Install core dependencies only"""
    print("📦 Installing core dependencies...")
    
    try:
        # Install core requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_core.txt"])
        
        print("✅ Core dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Setup basic environment"""
    print("⚙️ Setting up environment...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# Advanced Arbitrage Swarm Configuration
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_WALLET_ADDRESS=DYNnymGWfKKqYgwRuxYZq3f4qDtQ1LLaXogWhchHrjfQ
MIN_PROFIT_THRESHOLD=0.005
LOG_LEVEL=INFO
""")
        print("✅ Created .env configuration file")
    else:
        print("✅ Environment file already exists")
    
    return True

def test_installation():
    """Test core imports"""
    print("🧪 Testing installation...")
    
    try:
        import aiohttp
        import pandas
        import numpy
        import flask
        import requests
        print("✅ Core dependencies working!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Quick setup"""
    print_banner()
    
    if not install_core_dependencies():
        return False
    
    if not setup_environment():
        return False
    
    if not test_installation():
        return False
    
    print("\n🎯 SETUP COMPLETE!")
    print("=" * 80)
    print("Run the system:")
    print("python advanced_arbitrage_swarm.py")
    print("\nDashboard: http://localhost:8080")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Quick setup completed!")
        else:
            print("\n❌ Setup failed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
