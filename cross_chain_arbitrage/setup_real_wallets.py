"""
Setup script for Real Wallet Integration Dashboard
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.template'):
            print("📋 Creating .env file from template...")
            with open('.env.template', 'r') as template:
                content = template.read()
            with open('.env', 'w') as env_file:
                env_file.write(content)
            print("✅ .env file created!")
            print("🔧 Please edit .env file with your wallet addresses and API keys")
        else:
            print("⚠️ .env.template not found")
    else:
        print("✅ .env file already exists")

def main():
    print("🚀 REAL WALLET INTEGRATION SETUP")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Setup environment
    setup_environment()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your wallet info:")
    print("   - Solana wallet address")
    print("   - Ethereum wallet address") 
    print("   - Binance API keys")
    print("2. Run: python enhanced_dashboard.py")
    print("3. Open: http://localhost:5000")
    print("\n🔒 Security Note:")
    print("- Keep your .env file private")
    print("- Never commit API keys to version control")
    print("- Use read-only API keys when possible")

if __name__ == "__main__":
    main()
