#!/usr/bin/env python3
"""
Test Binance Testnet API Connection
"""

import asyncio
import aiohttp
import hmac
import hashlib
import time
import os

async def test_binance_testnet():
    """Test Binance testnet API with your credentials"""
    
    # Your credentials from .env
    api_key = "b50049a17061ba82b77baddd9aa9ed748fba0fecffa93486b3f4945a3f31e6cd"
    api_secret = "df5aed058f66c1be4a1fd19ff697228ee78b75d2964236101091b72724ace364"
    
    print("🔍 Testing Binance Testnet API Connection...")
    print(f"API Key: {api_key[:20]}...")
    print(f"API Secret: {api_secret[:20]}...")
    
    try:
        # Test 1: Basic connectivity
        print("\n📡 Test 1: Basic API connectivity...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api/v3/ping") as response:
                if response.status == 200:
                    print("✅ Binance testnet is reachable")
                else:
                    print(f"❌ Binance testnet unreachable: {response.status}")
                    return
        
        # Test 2: Server time
        print("\n⏰ Test 2: Server time sync...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api/v3/time") as response:
                if response.status == 200:
                    data = await response.json()
                    server_time = data['serverTime']
                    local_time = int(time.time() * 1000)
                    time_diff = abs(server_time - local_time)
                    print(f"✅ Server time: {server_time}, Local time: {local_time}")
                    print(f"📊 Time difference: {time_diff}ms")
                    
                    if time_diff > 5000:
                        print("⚠️ Warning: Time difference > 5 seconds, may cause signature issues")
                else:
                    print(f"❌ Cannot get server time: {response.status}")
                    return
        
        # Test 3: Account info with signature
        print("\n🔐 Test 3: Account info with signature...")
        
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
        headers = {
            'X-MBX-APIKEY': api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"📈 Response status: {response.status}")
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Successfully connected to Binance testnet!")
                    print(f"📊 Account type: {data.get('accountType', 'Unknown')}")
                    print(f"💰 Balances found: {len(data.get('balances', []))}")
                    
                    # Show non-zero balances
                    balances = data.get('balances', [])
                    non_zero_balances = [b for b in balances if float(b.get('free', 0)) > 0 or float(b.get('locked', 0)) > 0]
                    
                    if non_zero_balances:
                        print("\n💎 Your testnet balances:")
                        for balance in non_zero_balances:
                            asset = balance['asset']
                            free = float(balance['free'])
                            locked = float(balance['locked'])
                            total = free + locked
                            print(f"   {asset}: {total} (free: {free}, locked: {locked})")
                    else:
                        print("\n📭 No balances found in testnet account")
                        print("💡 To get testnet funds:")
                        print("   1. Visit: https://testnet.binance.vision/")
                        print("   2. Login with your testnet account")
                        print("   3. Use the faucet to get test USDT, BTC, ETH")
                        
                elif response.status == 401:
                    print("❌ Authentication failed!")
                    print("🔍 Checking error details...")
                    print(f"Response: {response_text}")
                    
                    if "API-key format invalid" in response_text:
                        print("🚨 API key format is invalid")
                    elif "Signature for this request is not valid" in response_text:
                        print("🚨 Signature validation failed")
                        print("💡 This could be due to:")
                        print("   - Incorrect API secret")
                        print("   - Time synchronization issues")
                        print("   - Wrong API endpoint")
                    elif "Invalid API-key" in response_text:
                        print("🚨 API key is not valid for testnet")
                        print("💡 Make sure you're using TESTNET API keys, not mainnet")
                else:
                    print(f"❌ Unexpected error: {response.status}")
                    print(f"Response: {response_text}")
        
        # Test 4: Exchange info (public endpoint)
        print("\n📋 Test 4: Exchange info (no auth required)...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://testnet.binance.vision/api/v3/exchangeInfo") as response:
                if response.status == 200:
                    data = await response.json()
                    symbols = data.get('symbols', [])
                    print(f"✅ Exchange info: {len(symbols)} trading pairs available")
                    print("📊 Sample pairs: BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, SOLUSDT")
                else:
                    print(f"❌ Cannot get exchange info: {response.status}")
                    
    except Exception as e:
        print(f"💥 Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_binance_testnet())
