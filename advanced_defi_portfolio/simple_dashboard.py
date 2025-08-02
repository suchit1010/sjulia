#!/usr/bin/env python3
"""
Simple Dashboard - Real Wallet Balances
Shows actual Solana wallet balances in a clean web interface
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from dotenv import load_dotenv
import threading
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

class SimpleWalletTracker:
    def __init__(self):
        self.solana_rpc = os.getenv('SOLANA_RPC_URL', 'https://api.devnet.solana.com')
        self.solana_wallet = os.getenv('SOLANA_WALLET_ADDRESS')
        self.portfolio_data = {
            'sol_balance': 0,
            'sol_price': 0,
            'sol_value': 0,
            'spl_tokens': [],
            'total_value': 0,
            'last_update': None
        }
        
    async def get_sol_price(self):
        """Get SOL price with fallback methods"""
        try:
            async with aiohttp.ClientSession() as session:
                # Try Jupiter API first
                try:
                    url = "https://price.jup.ag/v4/price?ids=SOL"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if 'data' in data and 'SOL' in data['data']:
                                return float(data['data']['SOL']['price'])
                except:
                    pass
                
                # Fallback to CoinGecko
                try:
                    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get('solana', {}).get('usd', 0)
                except:
                    pass
                
                # Final fallback - approximate current price
                return 95.0  # Approximate SOL price as fallback
                
        except Exception as e:
            print(f"Error getting SOL price: {e}")
            return 95.0  # Fallback price
    
    async def fetch_wallet_data(self):
        """Fetch real wallet data"""
        if not self.solana_wallet:
            return
            
        try:
            async with aiohttp.ClientSession() as session:
                # Get SOL balance
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [self.solana_wallet]
                }
                
                async with session.post(self.solana_rpc, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data and 'value' in data['result']:
                        lamports = data['result']['value']
                        sol_balance = lamports / 1e9
                        
                        # Get SOL price
                        sol_price = await self.get_sol_price()
                        sol_value = sol_balance * sol_price
                        
                        # Get SPL tokens
                        spl_tokens = await self.get_spl_tokens(session)
                        
                        # Update portfolio data
                        total_spl_value = sum(token['usd_value'] for token in spl_tokens)
                        
                        self.portfolio_data = {
                            'sol_balance': sol_balance,
                            'sol_price': sol_price,
                            'sol_value': sol_value,
                            'spl_tokens': spl_tokens,
                            'total_value': sol_value + total_spl_value,
                            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        print(f"💰 Portfolio updated: ${self.portfolio_data['total_value']:.2f}")
                        
        except Exception as e:
            print(f"Error fetching wallet data: {e}")
    
    async def get_spl_tokens(self, session):
        """Get SPL token balances"""
        tokens = []
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    self.solana_wallet,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            async with session.post(self.solana_rpc, json=payload) as response:
                data = await response.json()
                
                if 'result' in data and 'value' in data['result']:
                    for account in data['result']['value']:
                        try:
                            account_info = account['account']['data']['parsed']['info']
                            token_amount = account_info['tokenAmount']
                            mint = account_info['mint']
                            
                            amount = float(token_amount['uiAmount'] or 0)
                            if amount > 0:
                                # Known tokens for demonstration
                                token_info = self.get_token_info(mint)
                                usd_value = amount * token_info['price']
                                
                                tokens.append({
                                    'symbol': token_info['symbol'],
                                    'amount': amount,
                                    'price': token_info['price'],
                                    'usd_value': usd_value,
                                    'mint': mint[:8] + '...'
                                })
                        except:
                            continue
                            
        except Exception as e:
            print(f"Error getting SPL tokens: {e}")
            
        return tokens
    
    def get_token_info(self, mint):
        """Get token info with fallback data"""
        # Known tokens
        known_tokens = {
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v': {'symbol': 'USDC', 'price': 1.0},
            'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB': {'symbol': 'USDT', 'price': 1.0},
            '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R': {'symbol': 'RAY', 'price': 2.5},
            'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So': {'symbol': 'mSOL', 'price': 90.0},
        }
        
        return known_tokens.get(mint, {'symbol': f'TOKEN-{mint[:4]}', 'price': 0.1})

# Initialize wallet tracker
wallet_tracker = SimpleWalletTracker()

def update_portfolio_loop():
    """Background thread to update portfolio data"""
    while True:
        try:
            asyncio.run(wallet_tracker.fetch_wallet_data())
            time.sleep(30)  # Update every 30 seconds
        except Exception as e:
            print(f"Error in update loop: {e}")
            time.sleep(30)

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Solana Wallet Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    </style>
</head>
<body class="min-h-screen text-white">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold mb-2">💰 Solana Wallet Dashboard</h1>
            <p class="text-xl opacity-80">Real-time wallet balance tracking</p>
        </div>

        <!-- Portfolio Overview -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm opacity-80">Total Portfolio Value</p>
                        <p class="text-3xl font-bold" id="total-value">${{ data.total_value | round(2) }}</p>
                    </div>
                    <div class="text-4xl">💎</div>
                </div>
            </div>
            
            <div class="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm opacity-80">SOL Balance</p>
                        <p class="text-2xl font-bold">{{ data.sol_balance | round(4) }} SOL</p>
                        <p class="text-sm opacity-80">${{ data.sol_value | round(2) }}</p>
                    </div>
                    <div class="text-4xl">☀️</div>
                </div>
            </div>
            
            <div class="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm opacity-80">SPL Tokens</p>
                        <p class="text-2xl font-bold">{{ data.spl_tokens | length }}</p>
                        <p class="text-sm opacity-80">Different tokens</p>
                    </div>
                    <div class="text-4xl">🪙</div>
                </div>
            </div>
        </div>

        <!-- Token Holdings -->
        <div class="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">🪙 Token Holdings</h2>
            
            {% if data.spl_tokens %}
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-white border-opacity-20">
                            <th class="text-left py-3">Token</th>
                            <th class="text-right py-3">Amount</th>
                            <th class="text-right py-3">Price</th>
                            <th class="text-right py-3">Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="border-b border-white border-opacity-10">
                            <td class="py-3">
                                <div class="flex items-center">
                                    <span class="text-2xl mr-3">☀️</span>
                                    <div>
                                        <div class="font-semibold">SOL</div>
                                        <div class="text-sm opacity-70">Solana</div>
                                    </div>
                                </div>
                            </td>
                            <td class="text-right py-3">{{ data.sol_balance | round(4) }}</td>
                            <td class="text-right py-3">${{ data.sol_price | round(2) }}</td>
                            <td class="text-right py-3 font-semibold">${{ data.sol_value | round(2) }}</td>
                        </tr>
                        {% for token in data.spl_tokens %}
                        <tr class="border-b border-white border-opacity-10">
                            <td class="py-3">
                                <div class="flex items-center">
                                    <span class="text-2xl mr-3">🪙</span>
                                    <div>
                                        <div class="font-semibold">{{ token.symbol }}</div>
                                        <div class="text-sm opacity-70">{{ token.mint }}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="text-right py-3">{{ token.amount | round(2) }}</td>
                            <td class="text-right py-3">${{ token.price | round(4) }}</td>
                            <td class="text-right py-3 font-semibold">${{ token.usd_value | round(2) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-center opacity-70 py-8">No SPL tokens found</p>
            {% endif %}
        </div>

        <!-- Status -->
        <div class="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6 text-center">
            <p class="text-sm opacity-80">Last Updated: {{ data.last_update or 'Never' }}</p>
            <p class="text-xs opacity-60 mt-2">Wallet: {{ wallet_address[:8] }}...{{ wallet_address[-8:] }}</p>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setInterval(() => {
            window.location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template_string(
        DASHBOARD_HTML, 
        data=wallet_tracker.portfolio_data,
        wallet_address=wallet_tracker.solana_wallet or "Not configured"
    )

@app.route('/api/portfolio')
def api_portfolio():
    """API endpoint for portfolio data"""
    return jsonify(wallet_tracker.portfolio_data)

if __name__ == '__main__':
    print("🚀 Starting Simple Solana Wallet Dashboard...")
    print(f"💰 Wallet: {wallet_tracker.solana_wallet}")
    print(f"🌐 RPC: {wallet_tracker.solana_rpc}")
    print("-" * 50)
    
    # Start background update thread
    update_thread = threading.Thread(target=update_portfolio_loop, daemon=True)
    update_thread.start()
    
    # Initial data fetch
    asyncio.run(wallet_tracker.fetch_wallet_data())
    
    print("🌐 Dashboard: http://127.0.0.1:5001")
    print("📊 API: http://127.0.0.1:5001/api/portfolio")
    print("🔄 Auto-refresh: Every 30 seconds")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
