#!/usr/bin/env python3
"""
Test Binance Mainnet API Connection
"""

import asyncio
import aiohttp
import hmac
import hashlib
import time

async def test_binance_mainnet():
    """Test Binance mainnet API with your credentials"""
    
    # Your credentials
    api_key = "b50049a17061ba82b77baddd9aa9ed748fba0fecffa93486b3f4945a3f31e6cd"
    api_secret = "df5aed058f66c1be4a1fd19ff697228ee78b75d2964236101091b72724ace364"
    
    print("🔍 Testing Binance MAINNET API Connection...")
    print("⚠️ WARNING: This will connect to REAL Binance account!")
    print(f"API Key: {api_key[:20]}...")
    
    try:
        # Test account info
        print("\n🔐 Testing account access...")
        
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"https://api.binance.com/api/v3/account?{query_string}&signature={signature}"
        headers = {
            'X-MBX-APIKEY': api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"📈 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Successfully connected to Binance mainnet!")
                    print(f"📊 Account type: {data.get('accountType', 'Unknown')}")
                    
                    # Show non-zero balances
                    balances = data.get('balances', [])
                    non_zero_balances = [b for b in balances if float(b.get('free', 0)) > 0 or float(b.get('locked', 0)) > 0]
                    
                    if non_zero_balances:
                        print(f"\n💎 Your REAL account has {len(non_zero_balances)} assets:")
                        total_estimated_usd = 0
                        for balance in non_zero_balances[:10]:  # Show first 10
                            asset = balance['asset']
                            free = float(balance['free'])
                            locked = float(balance['locked'])
                            total = free + locked
                            print(f"   {asset}: {total:.6f} (free: {free:.6f}, locked: {locked:.6f})")
                        
                        if len(non_zero_balances) > 10:
                            print(f"   ... and {len(non_zero_balances) - 10} more assets")
                            
                    else:
                        print("\n📭 No balances found in your account")
                        
                elif response.status == 401:
                    response_text = await response.text()
                    print("❌ Authentication failed!")
                    print(f"Response: {response_text}")
                else:
                    response_text = await response.text()
                    print(f"❌ Unexpected error: {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"💥 Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_binance_mainnet())
