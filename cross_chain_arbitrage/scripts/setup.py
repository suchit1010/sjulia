"""
Setup script for Cross-Chain Arbitrage Swarm Bot
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        import sys
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ is required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check pip
    if not shutil.which("pip"):
        print("❌ pip is not installed")
        return False
    print("✅ pip is available")
    
    # Check git (optional but recommended)
    if shutil.which("git"):
        print("✅ git is available")
    else:
        print("⚠️ git is not available (optional)")
    
    return True

def setup_environment():
    """Set up the Python environment"""
    print("🐍 Setting up Python environment...")
    
    # Create virtual environment (optional)
    venv_choice = input("Create virtual environment? (y/n): ").lower().strip()
    if venv_choice == 'y':
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
        
        # Activate virtual environment
        if sys.platform == "win32":
            activate_cmd = ".\\venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print(f"💡 To activate virtual environment, run: {activate_cmd}")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        if not run_command(f"pip install -r {requirements_file}", "Installing dependencies from requirements.txt"):
            return False
    else:
        # Install essential packages manually
        essential_packages = [
            "flask>=2.3.0",
            "flask-cors>=4.0.0",
            "requests>=2.31.0",
            "aiohttp>=3.8.0",
            "web3>=6.0.0",
            "python-dotenv>=1.0.0",
            "loguru>=0.7.0",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0"
        ]
        
        for package in essential_packages:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                print(f"⚠️ Failed to install {package}, continuing...")
    
    return True

def setup_configuration():
    """Set up configuration files"""
    print("⚙️ Setting up configuration...")
    
    # Check if .env file exists
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found. Please create it with your configuration.")
        print("📝 Example .env content:")
        print("""
# JuliaOS Backend Configuration
JULIAOS_API_URL=http://localhost:8052
JULIAOS_API_KEY=your-secure-api-key-1

# AI/LLM Configuration
OPENAI_API_KEY=your_openai_key_here

# Blockchain RPC Configuration
SOLANA_DEVNET_RPC=https://api.devnet.solana.com
ETHEREUM_SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/your_alchemy_key

# Demo Configuration
USE_TESTNET=true
DEMO_MODE=true
""")
        return False
    else:
        print(f"✅ {env_file} found")
    
    return True

def verify_installation():
    """Verify the installation"""
    print("🔍 Verifying installation...")
    
    try:
        # Test imports
        import flask
        import requests
        import aiohttp
        print("✅ Core dependencies imported successfully")
        
        # Check if source files exist
        required_files = [
            "src/agents/solana_price_agent.py",
            "src/agents/ethereum_price_agent.py", 
            "src/agents/arbitrage_executor.py",
            "src/swarms/arbitrage_coordinator.py",
            "src/ui/app.py",
            "src/ui/templates/dashboard.html"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Cross-Chain Arbitrage Swarm Bot Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please install required tools.")
        return False
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed.")
        return False
    
    # Setup configuration
    if not setup_configuration():
        print("❌ Configuration setup failed.")
        return False
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed.")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start JuliaOS backend: cd ../backend && docker compose up")
    print("2. Configure your .env file with API keys")
    print("3. Run the demo: python scripts/run_demo.py")
    print("4. Open dashboard: http://localhost:5000")
    print("\n💡 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
