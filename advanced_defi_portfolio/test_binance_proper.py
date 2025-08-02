#!/usr/bin/env python3
"""
Proper Binance API Authentication Test
"""

import os
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

def test_binance_auth():
    """Test Binance API with proper authentication"""
    
    # Load from .env
    api_key = "b50049a17061ba82b77baddd9aa9ed748fba0fecffa93486b3f4945a3f31e6cd"
    api_secret = "df5aed058f66c1be4a1fd19ff697228ee78b75d2964236101091b72724ace364"
    
    print(f"🔍 Testing Binance API Authentication...")
    print(f"API Key: {api_key[:20]}...")
    print(f"Secret: {api_secret[:20]}...")
    
    # Test 1: Server Time (no auth required)
    print("\n📡 Step 1: Testing server connectivity...")
    try:
        response = requests.get("https://api.binance.com/api/v3/time")
        if response.status_code == 200:
            server_time = response.json()
            print(f"✅ Server time: {server_time}")
        else:
            print(f"❌ Server connectivity failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Server connectivity error: {e}")
        return
    
    # Test 2: Account Status (requires auth)
    print("\n🔐 Step 2: Testing account authentication...")
    
    timestamp = int(time.time() * 1000)
    params = {
        'timestamp': timestamp
    }
    
    # Create query string
    query_string = urlencode(params)
    
    # Create signature
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Add signature to params
    params['signature'] = signature
    
    headers = {
        'X-MBX-APIKEY': api_key
    }
    
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/account",
            params=params,
            headers=headers
        )
        
        print(f"📈 Response status: {response.status_code}")
        
        if response.status_code == 200:
            account_data = response.json()
            print("✅ Authentication successful!")
            print(f"Account type: {account_data.get('accountType', 'Unknown')}")
            print(f"Can trade: {account_data.get('canTrade', False)}")
            print(f"Can withdraw: {account_data.get('canWithdraw', False)}")
            
            # Show balances
            balances = account_data.get('balances', [])
            non_zero_balances = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
            
            if non_zero_balances:
                print(f"\n💰 Account balances ({len(non_zero_balances)} assets):")
                for balance in non_zero_balances[:10]:  # Show first 10
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    if total > 0:
                        print(f"  {balance['asset']}: {total:.8f} (free: {free:.8f}, locked: {locked:.8f})")
            else:
                print("\n💰 No balances found (empty account)")
                
        else:
            print("❌ Authentication failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request error: {e}")

    # Test 3: Test with testnet if mainnet fails
    print("\n🧪 Step 3: Testing with testnet (if mainnet failed)...")
    
    timestamp = int(time.time() * 1000)
    params = {
        'timestamp': timestamp
    }
    
    query_string = urlencode(params)
    signature = hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    
    try:
        response = requests.get(
            "https://testnet.binance.vision/api/v3/account",
            params=params,
            headers=headers
        )
        
        print(f"🧪 Testnet response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Testnet authentication successful!")
            account_data = response.json()
            balances = account_data.get('balances', [])
            non_zero_balances = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
            
            if non_zero_balances:
                print(f"💰 Testnet balances ({len(non_zero_balances)} assets):")
                for balance in non_zero_balances:
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    if total > 0:
                        print(f"  {balance['asset']}: {total:.8f}")
            else:
                print("💰 Empty testnet account")
        else:
            print("❌ Testnet authentication also failed!")
            try:
                error_data = response.json()
                print(f"Testnet error: {error_data}")
            except:
                print(f"Testnet response: {response.text}")
                
    except Exception as e:
        print(f"❌ Testnet request error: {e}")

if __name__ == "__main__":
    test_binance_auth()
