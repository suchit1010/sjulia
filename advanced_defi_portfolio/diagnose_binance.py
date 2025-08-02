#!/usr/bin/env python3
"""
Binance API Diagnostic Script
Helps identify issues with API keys and permissions
"""

import os
import hmac
import hashlib
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def diagnose_binance_api():
    """Comprehensive Binance API diagnosis"""
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    print("🔍 Binance API Diagnosis Report")
    print("=" * 50)
    
    # Check if keys exist
    print(f"📋 API Key provided: {'✅ Yes' if api_key else '❌ No'}")
    print(f"📋 API Secret provided: {'✅ Yes' if api_secret else '❌ No'}")
    
    if not api_key or not api_secret:
        print("❌ Missing API credentials!")
        return
    
    print(f"📋 API Key (first 20 chars): {api_key[:20]}...")
    print(f"📋 API Secret (first 20 chars): {api_secret[:20]}...")
    
    # Test 1: Basic connectivity
    print("\n🌐 Test 1: Basic Connectivity")
    try:
        response = requests.get("https://api.binance.com/api/v3/ping", timeout=10)
        print(f"✅ Binance API reachable: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach Binance API: {e}")
        return
    
    # Test 2: Server time
    print("\n⏰ Test 2: Server Time Sync")
    try:
        response = requests.get("https://api.binance.com/api/v3/time", timeout=10)
        server_time = response.json()['serverTime']
        local_time = int(time.time() * 1000)
        time_diff = abs(server_time - local_time)
        
        print(f"🕐 Server time: {server_time}")
        print(f"🕐 Local time: {local_time}")
        print(f"🕐 Time difference: {time_diff}ms")
        
        if time_diff > 5000:
            print("⚠️ WARNING: Time difference > 5 seconds! This can cause authentication issues.")
        else:
            print("✅ Time sync looks good")
            
    except Exception as e:
        print(f"❌ Cannot get server time: {e}")
    
    # Test 3: Public endpoint (no auth)
    print("\n📊 Test 3: Public Endpoint")
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
        if response.status_code == 200:
            btc_price = response.json()['price']
            print(f"✅ Public endpoint works. BTC price: ${btc_price}")
        else:
            print(f"❌ Public endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Public endpoint error: {e}")
    
    # Test 4: Test different signature methods
    print("\n🔐 Test 4: Authentication Methods")
    
    # Method 1: Simple account info
    test_simple_auth(api_key, api_secret)
    
    # Method 2: Account status
    test_account_status(api_key, api_secret)
    
    # Test 5: Check testnet
    print("\n🧪 Test 5: Testnet Access")
    test_testnet_access(api_key, api_secret)
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("1. Check if your API keys have 'Enable Reading' permission")
    print("2. Check if there are IP restrictions on your API keys")
    print("3. Verify the keys are active (not expired)")
    print("4. Try creating new API keys with proper permissions")
    print("5. Make sure your system clock is synchronized")

def test_simple_auth(api_key, api_secret):
    """Test simple authenticated request"""
    try:
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"https://api.binance.com/api/v3/account?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Method 1: Simple auth successful!")
            account_data = response.json()
            print(f"   Account type: {account_data.get('accountType', 'Unknown')}")
            print(f"   Can trade: {account_data.get('canTrade', 'Unknown')}")
            return True
        else:
            print(f"❌ Method 1: Simple auth failed - {response.status_code}")
            try:
                error_msg = response.json()
                print(f"   Error: {error_msg}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Method 1: Exception - {e}")
        return False

def test_account_status(api_key, api_secret):
    """Test account status endpoint"""
    try:
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"https://api.binance.com/api/v3/accountStatus?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Method 2: Account status successful!")
            return True
        else:
            print(f"❌ Method 2: Account status failed - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Method 2: Exception - {e}")
        return False

def test_testnet_access(api_key, api_secret):
    """Test testnet access"""
    try:
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        url = f"https://testnet.binance.vision/api/v3/account?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Testnet: Access successful!")
            return True
        else:
            print(f"❌ Testnet: Access failed - {response.status_code}")
            try:
                error_msg = response.json()
                print(f"   Testnet error: {error_msg}")
            except:
                print(f"   Testnet raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Testnet: Exception - {e}")
        return False

if __name__ == "__main__":
    diagnose_binance_api()
