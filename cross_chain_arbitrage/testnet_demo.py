#!/usr/bin/env python3
"""
Testnet Demo Script - Real APIs with Test Funds
Demonstrates testnet trading with Solana Devnet, Ethereum Sepolia, and Paper Trading
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from secure_trading_interface import RealTradingInterface, WalletConfig, setup_testnet_configuration

async def testnet_demo():
    """Run a comprehensive testnet demonstration"""
    print("🧪 TESTNET TRADING DEMO")
    print("=" * 60)
    print("🔗 Real blockchain connections with test funds")
    print("📡 Live API integrations (paper trading)")
    print("🎯 Perfect for strategy development")
    print("=" * 60)
    
    # Create testnet wallets
    testnet_wallets = {
        "solana": WalletConfig(
            address="DevNet_9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL",
            chain="solana",
            rpc_url="https://api.devnet.solana.com"
        ),
        "ethereum": WalletConfig(
            address="0xSepolia_742d35Cc6C0C4532164a2f8e22a07eDb",
            chain="ethereum", 
            rpc_url="https://sepolia.infura.io/v3/testnet"
        )
    }
    
    # Initialize trading interface in testnet mode
    print("\n🔄 Initializing testnet trading interface...")
    trading_interface = RealTradingInterface(testnet_wallets, demo_mode=False, testnet_mode=True)
    
    print("\n📊 TESTNET PORTFOLIO STATUS:")
    print("-" * 40)
    
    # Get comprehensive portfolio status
    status = await trading_interface.get_comprehensive_wallet_status()
    
    print(f"🆔 Session ID: {status['session_id']}")
    print(f"🧪 Testnet Mode: Active")
    print(f"⏰ Timestamp: {status['timestamp']}")
    print(f"💰 Total Portfolio: ${status['total_portfolio_value']:.2f}")
    
    print("\n💼 Testnet Wallet Details:")
    for chain, wallet_info in status["wallets"].items():
        if "error" in wallet_info:
            print(f"❌ {chain.upper()}: {wallet_info['error']}")
        else:
            balance = wallet_info["balance"]
            usd_value = wallet_info.get("usd_value", 0)
            rpc_url = testnet_wallets[chain].rpc_url
            print(f"✅ {chain.upper()}: {balance['balance']:.4f} {balance['token']} (${usd_value:.2f})")
            print(f"   🔗 RPC: {rpc_url}")
    
    print("\n📈 TESTNET PRICE FEEDS:")
    print("-" * 40)
    
    prices = await trading_interface.get_real_prices()
    for chain, price_info in prices.items():
        price = price_info.get("price", "N/A")
        source = price_info.get("source", "unknown")
        print(f"💲 {chain.upper()}: ${price} (source: {source})")
        
        if "testnet" in source or "devnet" in source:
            print(f"   🧪 Using testnet price feed")
    
    print("\n⛽ TESTNET GAS ESTIMATES:")
    print("-" * 40)
    
    for chain in ["ethereum", "solana"]:
        try:
            gas_info = await trading_interface.estimate_gas_fees(chain)
            cost = gas_info.get("estimated_cost_usd", "N/A")
            print(f"⛽ {chain.upper()}: ${cost} (testnet estimate)")
        except Exception as e:
            print(f"⛽ {chain.upper()}: Error - {e}")
    
    print("\n🚀 TESTNET ARBITRAGE TRADES:")
    print("-" * 40)
    
    # Create testnet-specific arbitrage opportunities
    testnet_opportunities = [
        {
            "name": "SOL Devnet → ETH Sepolia",
            "from_chain": "solana",
            "to_chain": "ethereum",
            "amount": 500.0,  # Higher amounts OK for testnet
            "expected_profit": 45.75,
            "price_difference": 2.8,
            "confidence": 0.89
        },
        {
            "name": "ETH Sepolia → SOL Devnet", 
            "from_chain": "ethereum",
            "to_chain": "solana",
            "amount": 2.0,
            "expected_profit": 38.40,
            "price_difference": 3.1,
            "confidence": 0.91
        },
        {
            "name": "Large Testnet Trade",
            "from_chain": "solana", 
            "to_chain": "ethereum",
            "amount": 1000.0,  # Large amounts for testnet testing
            "expected_profit": 85.25,
            "price_difference": 4.2,
            "confidence": 0.95
        }
    ]
    
    successful_trades = 0
    total_profit = 0.0
    
    for i, opportunity in enumerate(testnet_opportunities, 1):
        print(f"\n📋 Testnet Trade {i}: {opportunity['name']}")
        print(f"   Amount: {opportunity['amount']} {opportunity['from_chain'].upper()}")
        print(f"   Expected Profit: ${opportunity['expected_profit']:.2f}")
        print(f"   Confidence: {opportunity['confidence']:.0%}")
        print(f"   🧪 Testnet Transaction (no real funds)")
        
        # Execute the testnet trade
        result = await trading_interface.execute_arbitrage_trade(opportunity)
        
        if result["success"]:
            successful_trades += 1
            profit = result.get("profit", 0)
            total_profit += profit
            print(f"   ✅ Testnet Success! Simulated Profit: ${profit:.2f}")
            print(f"   🆔 Trade ID: {result['trade_id']}")
            if "from_hash" in result:
                print(f"   🔗 Testnet TX: {result.get('from_hash', 'N/A')}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 TESTNET SESSION SUMMARY:")
    print("-" * 40)
    print(f"🎯 Testnet Trades: {len(testnet_opportunities)}")
    print(f"✅ Successful: {successful_trades}")
    print(f"💰 Total Simulated Profit: ${total_profit:.2f}")
    print(f"📈 Success Rate: {(successful_trades/len(testnet_opportunities)*100):.1f}%")
    
    # Show testnet advantages
    print(f"\n🧪 TESTNET ADVANTAGES:")
    print("-" * 40)
    print("✅ Real blockchain connections (devnet/sepolia)")
    print("✅ Actual API integrations")
    print("✅ No real funds at risk")
    print("✅ Higher trading limits for testing")
    print("✅ Perfect for strategy development")
    print("✅ Learn without financial risk")
    
    # Show how to get testnet tokens
    print(f"\n💧 GET TESTNET TOKENS:")
    print("-" * 40)
    print("🪙 Solana Devnet SOL:")
    print("   https://faucet.solana.com")
    print("   solana airdrop 2 <your-address> --url devnet")
    
    print("\n💎 Ethereum Sepolia ETH:")
    print("   https://sepoliafaucet.com")
    print("   https://faucet.sepolia.dev")
    
    print("\n📊 Paper Trading:")
    print("   Binance Testnet: https://testnet.binance.vision")
    print("   Coinbase Sandbox: https://docs.pro.coinbase.com")
    
    print(f"\n🎉 TESTNET DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Ready for real strategy development")
    print("✅ All testnet features demonstrated")
    print("💡 Perfect environment for learning")
    print("🚀 Upgrade to mainnet when ready")

if __name__ == "__main__":
    print("🧪 Starting comprehensive testnet demo...")
    try:
        asyncio.run(testnet_demo())
    except KeyboardInterrupt:
        print("\n\n👋 Testnet demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Testnet demo error: {e}")
        import traceback
        traceback.print_exc()
