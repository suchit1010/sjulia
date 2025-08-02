#!/usr/bin/env python3
"""
Simple Wallet Integration Test
Test real Solana wallet balance fetching
"""

import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_solana_wallet():
    """Test Solana wallet balance fetching"""
    
    solana_rpc = os.getenv('SOLANA_RPC_URL', 'https://api.devnet.solana.com')
    solana_wallet = os.getenv('SOLANA_WALLET_ADDRESS')
    
    print(f"🔍 Testing Solana Wallet Integration")
    print(f"RPC: {solana_rpc}")
    print(f"Wallet: {solana_wallet}")
    print("-" * 50)
    
    if not solana_wallet:
        print("❌ No Solana wallet address configured!")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Get SOL balance
            print("📊 Getting SOL balance...")
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [solana_wallet]
            }
            
            async with session.post(solana_rpc, json=payload) as response:
                data = await response.json()
                print(f"Response: {data}")
                
                if 'result' in data and 'value' in data['result']:
                    lamports = data['result']['value']
                    sol_balance = lamports / 1e9
                    print(f"✅ SOL Balance: {sol_balance} SOL (Lamports: {lamports})")
                    
                    # Get SOL price
                    print("💰 Getting SOL price...")
                    price_url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
                    async with session.get(price_url) as price_response:
                        price_data = await price_response.json()
                        sol_price = price_data.get('solana', {}).get('usd', 0)
                        usd_value = sol_balance * sol_price
                        
                        print(f"💲 SOL Price: ${sol_price}")
                        print(f"💵 Total Value: ${usd_value:.2f}")
                else:
                    print(f"❌ Failed to get balance: {data}")
            
            # Test 2: Get SPL token accounts
            print("\n🪙 Getting SPL token accounts...")
            spl_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    solana_wallet,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            async with session.post(solana_rpc, json=spl_payload) as response:
                data = await response.json()
                
                if 'result' in data and 'value' in data['result']:
                    accounts = data['result']['value']
                    print(f"✅ Found {len(accounts)} SPL token accounts")
                    
                    for i, account in enumerate(accounts[:5]):  # Show first 5
                        try:
                            info = account['account']['data']['parsed']['info']
                            mint = info['mint']
                            amount = info['tokenAmount']['uiAmount']
                            print(f"  Token {i+1}: {mint[:8]}... Amount: {amount}")
                        except:
                            continue
                else:
                    print(f"❌ Failed to get SPL tokens: {data}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_solana_wallet())
