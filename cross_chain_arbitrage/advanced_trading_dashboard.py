"""
Advanced Trading Dashboard for Cross-Chain Arbitrage
Integrates with secure trading interface for real-time monitoring
"""
import asyncio
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import threading
import time
from secure_trading_interface import RealTradingInterface, setup_secure_trading

app = Flask(__name__)
CORS(app)

# Global trading interface
trading_interface = None
dashboard_data = {
    "portfolio": {},
    "trades": [],
    "stats": {},
    "prices": {},
    "last_update": ""
}

# Enhanced HTML template with dark theme and modern design
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cross-Chain Arbitrage Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #e2e8f0;
        }
        
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        .gradient-border {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2px;
            border-radius: 12px;
        }
        
        .status-online {
            background: linear-gradient(45deg, #10b981, #34d399);
        }
        
        .status-offline {
            background: linear-gradient(45deg, #ef4444, #f87171);
        }
        
        .profit-positive {
            color: #10b981;
        }
        
        .profit-negative {
            color: #ef4444;
        }
        
        .animate-pulse-slow {
            animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
    </style>
</head>
<body class="font-mono">
    <div class="min-h-screen p-4">
        <!-- Header -->
        <div class="gradient-border mb-6">
            <div class="glass-card rounded-xl p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                            Cross-Chain Arbitrage Dashboard
                        </h1>
                        <p class="text-slate-400 mt-2">Real-time trading interface with enhanced security</p>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div id="connectionStatus" class="px-4 py-2 rounded-full text-white font-bold status-offline">
                            Disconnected
                        </div>
                        <div class="text-right">
                            <div class="text-sm text-slate-400">Last Update</div>
                            <div id="lastUpdate" class="font-bold">--:--:--</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Trading Controls -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <!-- Portfolio Overview -->
            <div class="glass-card rounded-xl p-6">
                <h2 class="text-xl font-bold mb-4 text-blue-400">💼 Portfolio</h2>
                <div id="portfolioContent">
                    <div class="text-center text-slate-400">Loading portfolio...</div>
                </div>
            </div>

            <!-- Trading Statistics -->
            <div class="glass-card rounded-xl p-6">
                <h2 class="text-xl font-bold mb-4 text-green-400">📊 Statistics</h2>
                <div id="statsContent">
                    <div class="text-center text-slate-400">Loading statistics...</div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="glass-card rounded-xl p-6">
                <h2 class="text-xl font-bold mb-4 text-purple-400">🚀 Quick Actions</h2>
                <div class="space-y-3">
                    <button onclick="executeDemo()" 
                            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300">
                        🎭 Execute Demo Trade
                    </button>
                    <button onclick="executeReal()" 
                            class="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300">
                        💰 Execute Real Trade
                    </button>
                    <button onclick="refreshData()" 
                            class="w-full bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300">
                        🔄 Refresh Data
                    </button>
                </div>
            </div>
        </div>

        <!-- Price Charts and Trade History -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Price Chart -->
            <div class="glass-card rounded-xl p-6">
                <h2 class="text-xl font-bold mb-4 text-yellow-400">📈 Price Trends</h2>
                <canvas id="priceChart" width="400" height="200"></canvas>
            </div>

            <!-- Trade History -->
            <div class="glass-card rounded-xl p-6">
                <h2 class="text-xl font-bold mb-4 text-red-400">📋 Recent Trades</h2>
                <div id="tradeHistory" class="space-y-3 max-h-64 overflow-y-auto">
                    <div class="text-center text-slate-400">No trades yet...</div>
                </div>
            </div>
        </div>

        <!-- Status Messages -->
        <div id="statusMessages" class="fixed bottom-4 right-4 space-y-2 z-50">
        </div>
    </div>

    <script>
        let priceChart;
        let priceData = {
            solana: [],
            ethereum: []
        };

        // Initialize price chart
        function initPriceChart() {
            const ctx = document.getElementById('priceChart').getContext('2d');
            priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'SOL Price',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'ETH Price',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#e2e8f0'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#94a3b8'
                            },
                            grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#94a3b8'
                            },
                            grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        // Show status message
        function showMessage(message, type = 'info') {
            const colors = {
                success: 'from-green-500 to-emerald-600',
                error: 'from-red-500 to-pink-600',
                info: 'from-blue-500 to-purple-600',
                warning: 'from-yellow-500 to-orange-600'
            };

            const messageDiv = document.createElement('div');
            messageDiv.className = `bg-gradient-to-r ${colors[type]} text-white px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300`;
            messageDiv.innerHTML = message;

            document.getElementById('statusMessages').appendChild(messageDiv);

            setTimeout(() => {
                messageDiv.style.transform = 'translateX(100%)';
                setTimeout(() => messageDiv.remove(), 300);
            }, 3000);
        }

        // Execute demo trade
        async function executeDemo() {
            try {
                showMessage('🎭 Executing demo trade...', 'info');
                const response = await fetch('/api/execute_demo', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`✅ Demo trade completed! Profit: $${result.profit.toFixed(2)}`, 'success');
                } else {
                    showMessage(`❌ Demo trade failed: ${result.error}`, 'error');
                }
                
                refreshData();
            } catch (error) {
                showMessage(`❌ Error: ${error.message}`, 'error');
            }
        }

        // Execute real trade
        async function executeReal() {
            if (!confirm('⚠️ This will execute a REAL trade with actual funds. Are you sure?')) {
                return;
            }

            try {
                showMessage('💰 Executing real trade...', 'warning');
                const response = await fetch('/api/execute_real', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`✅ Real trade completed! Profit: $${result.profit.toFixed(2)}`, 'success');
                } else {
                    showMessage(`❌ Real trade failed: ${result.error}`, 'error');
                }
                
                refreshData();
            } catch (error) {
                showMessage(`❌ Error: ${error.message}`, 'error');
            }
        }

        // Refresh dashboard data
        async function refreshData() {
            try {
                const response = await fetch('/api/dashboard_data');
                const data = await response.json();
                
                updatePortfolio(data.portfolio);
                updateStatistics(data.stats);
                updateTradeHistory(data.trades);
                updatePriceChart(data.prices);
                
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                document.getElementById('connectionStatus').textContent = 'Connected';
                document.getElementById('connectionStatus').className = 'px-4 py-2 rounded-full text-white font-bold status-online';
                
            } catch (error) {
                console.error('Failed to refresh data:', error);
                document.getElementById('connectionStatus').textContent = 'Disconnected';
                document.getElementById('connectionStatus').className = 'px-4 py-2 rounded-full text-white font-bold status-offline';
            }
        }

        // Update portfolio display
        function updatePortfolio(portfolio) {
            const content = document.getElementById('portfolioContent');
            
            if (!portfolio.wallets) {
                content.innerHTML = '<div class="text-center text-slate-400">No portfolio data</div>';
                return;
            }

            let html = `
                <div class="text-2xl font-bold mb-4 text-green-400">$${portfolio.total_portfolio_value.toFixed(2)}</div>
            `;

            for (const [chain, wallet] of Object.entries(portfolio.wallets)) {
                const status = wallet.error ? '❌' : '✅';
                const balance = wallet.balance ? wallet.balance.balance.toFixed(4) : '0.0000';
                const token = wallet.balance ? wallet.balance.token : 'N/A';
                const usdValue = wallet.usd_value ? wallet.usd_value.toFixed(2) : '0.00';

                html += `
                    <div class="flex justify-between items-center mb-2 p-2 rounded bg-slate-800/50">
                        <span>${status} ${chain.toUpperCase()}</span>
                        <div class="text-right">
                            <div>${balance} ${token}</div>
                            <div class="text-sm text-slate-400">$${usdValue}</div>
                        </div>
                    </div>
                `;
            }

            content.innerHTML = html;
        }

        // Update statistics display
        function updateStatistics(stats) {
            const content = document.getElementById('statsContent');
            
            if (!stats) {
                content.innerHTML = '<div class="text-center text-slate-400">No statistics available</div>';
                return;
            }

            const profitClass = stats.total_profit >= 0 ? 'profit-positive' : 'profit-negative';
            
            const html = `
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span>Total Trades:</span>
                        <span class="font-bold">${stats.total_trades || 0}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Success Rate:</span>
                        <span class="font-bold">${(stats.success_rate || 0).toFixed(1)}%</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Total Profit:</span>
                        <span class="font-bold ${profitClass}">$${(stats.total_profit || 0).toFixed(2)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Recent 24h:</span>
                        <span class="font-bold">${stats.recent_24h || 0} trades</span>
                    </div>
                </div>
            `;

            content.innerHTML = html;
        }

        // Update trade history
        function updateTradeHistory(trades) {
            const content = document.getElementById('tradeHistory');
            
            if (!trades || trades.length === 0) {
                content.innerHTML = '<div class="text-center text-slate-400">No trades yet...</div>';
                return;
            }

            let html = '';
            trades.slice(-10).reverse().forEach(trade => {
                const statusIcon = trade.status.includes('completed') ? '✅' : 
                                 trade.status.includes('failed') ? '❌' : '⏳';
                const profitClass = trade.profit >= 0 ? 'profit-positive' : 'profit-negative';

                html += `
                    <div class="p-3 rounded bg-slate-800/50 border-l-4 border-blue-500">
                        <div class="flex justify-between items-start">
                            <div>
                                <div class="font-bold">${statusIcon} ${trade.from_chain.toUpperCase()} → ${trade.to_chain.toUpperCase()}</div>
                                <div class="text-sm text-slate-400">${new Date(trade.timestamp).toLocaleString()}</div>
                            </div>
                            <div class="text-right">
                                <div class="${profitClass} font-bold">$${trade.profit.toFixed(2)}</div>
                                <div class="text-sm text-slate-400">${trade.amount.toFixed(2)} ${trade.from_chain}</div>
                            </div>
                        </div>
                    </div>
                `;
            });

            content.innerHTML = html;
        }

        // Update price chart
        function updatePriceChart(prices) {
            if (!priceChart || !prices) return;

            const now = new Date().toLocaleTimeString();
            
            // Add new data points
            if (prices.solana && prices.solana.price) {
                priceData.solana.push(prices.solana.price);
                priceChart.data.labels.push(now);
            }

            // Keep only last 20 data points
            if (priceChart.data.labels.length > 20) {
                priceChart.data.labels.shift();
                priceData.solana.shift();
            }

            priceChart.data.datasets[0].data = priceData.solana;
            priceChart.update();
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initPriceChart();
            refreshData();
            
            // Auto-refresh every 10 seconds
            setInterval(refreshData, 10000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/dashboard_data')
def get_dashboard_data():
    """Get current dashboard data"""
    return jsonify(dashboard_data)

@app.route('/api/execute_demo', methods=['POST'])
def execute_demo():
    """Execute a demo arbitrage trade"""
    if not trading_interface:
        return jsonify({"success": False, "error": "Trading interface not initialized"})
    
    # Create demo opportunity
    demo_opportunity = {
        "from_chain": "solana",
        "to_chain": "ethereum",
        "amount": 100.0,
        "expected_profit": 25.50,
        "price_difference": 2.5,
        "confidence": 0.85
    }
    
    try:
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(trading_interface.execute_arbitrage_trade(demo_opportunity))
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/execute_real', methods=['POST'])
def execute_real():
    """Execute a real arbitrage trade"""
    if not trading_interface:
        return jsonify({"success": False, "error": "Trading interface not initialized"})
    
    if trading_interface.demo_mode:
        return jsonify({"success": False, "error": "Real trading not available in demo mode"})
    
    # Create real opportunity (smaller amount for safety)
    real_opportunity = {
        "from_chain": "solana",
        "to_chain": "ethereum",
        "amount": 50.0,
        "expected_profit": 12.75,
        "price_difference": 1.5,
        "confidence": 0.90
    }
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(trading_interface.execute_arbitrage_trade(real_opportunity))
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

async def update_dashboard_data():
    """Update dashboard data periodically"""
    global dashboard_data, trading_interface
    
    while True:
        try:
            if trading_interface:
                # Get portfolio status
                portfolio = await trading_interface.get_comprehensive_wallet_status()
                
                # Get trading statistics
                stats = await trading_interface.get_trading_statistics()
                
                # Get price data
                prices = await trading_interface.get_real_prices()
                
                # Update dashboard data
                dashboard_data.update({
                    "portfolio": portfolio,
                    "trades": stats.get("recent_trades", []),
                    "stats": stats,
                    "prices": prices,
                    "last_update": datetime.now().isoformat()
                })
                
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
            await asyncio.sleep(10)

def run_dashboard_updater():
    """Run the dashboard updater in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_dashboard_data())

def start_dashboard(interface):
    """Start the dashboard with the given trading interface"""
    global trading_interface
    trading_interface = interface
    
    # Start dashboard data updater in background
    updater_thread = threading.Thread(target=run_dashboard_updater, daemon=True)
    updater_thread.start()
    
    print("\n🌐 Starting Advanced Trading Dashboard...")
    print("📊 Access your dashboard at: http://localhost:5000")
    print("🔄 Real-time updates enabled")
    print("🎨 Enhanced UI with dark theme")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    print("🚀 Cross-Chain Arbitrage Advanced Dashboard")
    print("Setting up trading interface...")
    
    # Setup trading interface
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    wallets, demo_mode = setup_secure_trading()
    if wallets:
        interface = RealTradingInterface(wallets, demo_mode)
        start_dashboard(interface)
    else:
        print("❌ Failed to setup trading interface")
