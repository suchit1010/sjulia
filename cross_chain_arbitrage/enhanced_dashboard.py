"""
Enhanced Cross-Chain Arbitrage Dashboard - Real Wallet Integration
"""
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import os
import time
from datetime import datetime
import threading
import asyncio
import logging

# Import real wallet integrations
from simple_wallet_manager import wallet_manager
import trading_execution_agent

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced dark theme dashboard template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cross-Chain Arbitrage Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            --danger-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            --dark-bg: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #2d2d2d 100%);
            --card-bg: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            --text-primary: white;
            --text-secondary: #b0b0b0;
            --border-color: rgba(255,255,255,0.1);
        }
        
        body {
            background: var(--dark-bg);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        
        .navbar {
            background: var(--primary-gradient);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
        }
        
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .status-card {
            min-height: 140px;
        }
        
        .gradient-card {
            color: white;
            border: none;
        }
        
        .primary-card {
            background: var(--primary-gradient);
        }
        
        .secondary-card {
            background: var(--secondary-gradient);
        }
        
        .success-card {
            background: var(--success-gradient);
        }
        
        .warning-card {
            background: var(--warning-gradient);
        }
        
        .danger-card {
            background: var(--danger-gradient);
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 10px 0;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .btn-custom {
            border-radius: 25px;
            padding: 8px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            margin: 0 5px;
        }
        
        .btn-start {
            background: var(--success-gradient);
            color: white;
        }
        
        .btn-stop {
            background: var(--danger-gradient);
            color: white;
        }
        
        .btn-custom:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .table-dark {
            background: var(--card-bg);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .table-dark th {
            background: var(--primary-gradient);
            border: none;
            color: white;
        }
        
        .table-dark td {
            border-color: var(--border-color);
            vertical-align: middle;
        }
        
        .badge-success {
            background: var(--success-gradient) !important;
            border: none;
            padding: 5px 10px;
            border-radius: 15px;
        }
        
        .profit-positive {
            color: #00f2fe;
            font-weight: bold;
        }
        
        .profit-negative {
            color: #f5576c;
            font-weight: bold;
        }
        
        .price-display {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .spread-indicator {
            font-size: 1.5rem;
            font-weight: bold;
            padding: 10px;
            border-radius: 10px;
            background: var(--warning-gradient);
            color: #000;
            text-align: center;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-running {
            background: #00f2fe;
        }
        
        .status-stopped {
            background: #f5576c;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .header-title {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        @media (max-width: 768px) {
            .metric-value {
                font-size: 1.8rem;
            }
            .header-title {
                font-size: 1.8rem;
            }
            .chart-container {
                height: 250px;
            }
            .card {
                margin-bottom: 15px;
            }
        }
        
        @media (max-width: 576px) {
            .metric-value {
                font-size: 1.5rem;
            }
            .btn-custom {
                padding: 6px 15px;
                font-size: 0.9rem;
            }
            .chart-container {
                height: 200px;
            }
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-rocket me-2"></i>Cross-Chain Arbitrage
            </span>
            <div class="d-flex align-items-center">
                <span class="status-indicator" id="statusIndicator"></span>
                <span id="connectionStatus">Connected</span>
            </div>
        </div>
    </nav>

    <div class="container-fluid px-4">
        <h1 class="header-title">
            <i class="fas fa-chart-line me-3"></i>Trading Dashboard
        </h1>
        
        <!-- Status Cards Row -->
        <div class="row g-4">
            <div class="col-xl-3 col-lg-6 col-md-6">
                <div class="card gradient-card primary-card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-robot fa-2x mb-3"></i>
                        <h5 class="card-title">Bot Status</h5>
                        <div class="metric-value" id="botStatus">Stopped</div>
                        <div class="mt-3">
                            <button class="btn btn-custom btn-start" onclick="startBot()">
                                <i class="fas fa-play me-2"></i>Start
                            </button>
                            <button class="btn btn-custom btn-stop" onclick="stopBot()">
                                <i class="fas fa-stop me-2"></i>Stop
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-xl-3 col-lg-6 col-md-6">
                <div class="card gradient-card secondary-card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-exchange-alt fa-2x mb-3"></i>
                        <h5 class="card-title">Total Trades</h5>
                        <div class="metric-value" id="totalTrades">0</div>
                        <div class="metric-label">Executed Successfully</div>
                    </div>
                </div>
            </div>
            
            <div class="col-xl-3 col-lg-6 col-md-6">
                <div class="card gradient-card success-card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-dollar-sign fa-2x mb-3"></i>
                        <h5 class="card-title">Total Profit</h5>
                        <div class="metric-value" id="totalProfit">$0.00</div>
                        <div class="metric-label">Net P&L</div>
                    </div>
                </div>
            </div>
            
            <div class="col-xl-3 col-lg-6 col-md-6">
                <div class="card gradient-card warning-card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x mb-3"></i>
                        <h5 class="card-title">Last Update</h5>
                        <div class="metric-value" style="font-size: 1.5rem;" id="lastUpdate">Never</div>
                        <div class="metric-label">System Time</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Charts and Prices Row -->
        <div class="row g-4 mt-2">
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-chart-area me-2"></i>Real-time Price Monitoring
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="priceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-coins me-2"></i>Current Prices
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-4">
                            <div class="d-flex align-items-center mb-2">
                                <i class="fab fa-solana me-2 text-primary"></i>
                                <strong >Solana (Raydium)</strong>
                            </div>
                            <div class="price-display text-primary" id="solanaPrice">$0.0000</div>
                        </div>
                        
                        <div class="mb-4">
                            <div class="d-flex align-items-center mb-2">
                                <i class="fab fa-ethereum me-2 text-info"></i>
                                <strong>Ethereum (Uniswap)</strong>
                            </div>
                            <div class="price-display text-info" id="ethereumPrice">$0.0000</div>
                        </div>
                        
                        <div>
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-percentage me-2"></i>
                                <strong>Price Spread</strong>
                            </div>
                            <div class="spread-indicator" id="priceSpread">0.00%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Trades Table Row -->
        <div class="row g-4 mt-2">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">
                            <i class="fas fa-history me-2"></i>Recent Trades
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-dark table-hover">
                                <thead>
                                    <tr>
                                        <th><i class="fas fa-hashtag me-2"></i>Trade ID</th>
                                        <th><i class="fas fa-clock me-2"></i>Time</th>
                                        <th><i class="fas fa-arrows-alt me-2"></i>Direction</th>
                                        <th><i class="fas fa-dollar-sign me-2"></i>Amount</th>
                                        <th><i class="fas fa-chart-line me-2"></i>Profit</th>
                                        <th><i class="fas fa-check me-2"></i>Status</th>
                                    </tr>
                                </thead>
                                <tbody id="tradesBody">
                                    <tr>
                                        <td colspan="6" class="text-center py-4">
                                            <i class="fas fa-hourglass-half me-2"></i>No trades executed yet
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize price chart with dark theme
        const ctx = document.getElementById('priceChart').getContext('2d');
        const priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Solana Price',
                    data: [],
                    borderColor: '#4facfe',
                    backgroundColor: 'rgba(79, 172, 254, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Ethereum Price', 
                    data: [],
                    borderColor: '#f5576c',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff',
                            font: {
                                size: 14
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#b0b0b0'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#b0b0b0',
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        function updateDashboard() {
            // Update main status
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update status indicator
                    const statusIndicator = document.getElementById('statusIndicator');
                    const botStatus = document.getElementById('botStatus');
                    
                    if (data.running) {
                        statusIndicator.className = 'status-indicator status-running';
                        botStatus.textContent = 'Running';
                    } else {
                        statusIndicator.className = 'status-indicator status-stopped';
                        botStatus.textContent = 'Stopped';
                    }
                    
                    // Update metrics
                    document.getElementById('totalTrades').textContent = data.trades_executed || 0;
                    const profit = data.total_profit || 0;
                    document.getElementById('totalProfit').textContent = '$' + profit.toFixed(2);
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                    
                    // Update prices with real data
                    if (data.price_data && data.price_data.solana && data.price_data.ethereum) {
                        const solPrice = data.price_data.solana.price;
                        const ethPrice = data.price_data.ethereum.price;
                        const solBalance = data.price_data.solana.balance || 0;
                        const ethBalance = data.price_data.ethereum.balance || 0;
                        
                        document.getElementById('solanaPrice').innerHTML = `
                            <div>$${solPrice.toFixed(4)}</div>
                            <div style="font-size: 0.8rem; color: #888;">Balance: ${solBalance.toFixed(4)} SOL</div>
                        `;
                        
                        document.getElementById('ethereumPrice').innerHTML = `
                            <div>$${ethPrice.toFixed(4)}</div>
                            <div style="font-size: 0.8rem; color: #888;">Balance: ${ethBalance.toFixed(4)} ETH</div>
                        `;
                        
                        const spread = Math.abs(ethPrice - solPrice) / Math.min(solPrice, ethPrice) * 100;
                        document.getElementById('priceSpread').textContent = spread.toFixed(2) + '%';
                        
                        // Update chart
                        const now = new Date().toLocaleTimeString();
                        priceChart.data.labels.push(now);
                        priceChart.data.datasets[0].data.push(solPrice);
                        priceChart.data.datasets[1].data.push(ethPrice);
                        
                        // Keep only last 20 points
                        if (priceChart.data.labels.length > 20) {
                            priceChart.data.labels.shift();
                            priceChart.data.datasets[0].data.shift();
                            priceChart.data.datasets[1].data.shift();
                        }
                        
                        priceChart.update('none'); // Smooth update
                    }
                    
                    // Show wallet connection status
                    if (data.wallet_data) {
                        let walletStatus = 'Wallets: ';
                        if (data.wallet_data.solana) walletStatus += 'SOL ✓ ';
                        if (data.wallet_data.ethereum) walletStatus += 'ETH ✓ ';
                        if (data.wallet_data.binance) walletStatus += 'BIN ✓ ';
                        
                        // Update portfolio value if available
                        if (data.portfolio_value > 0) {
                            document.getElementById('totalProfit').innerHTML = `
                                <div>$${data.portfolio_value.toFixed(2)}</div>
                                <div style="font-size: 0.8rem;">Portfolio Value</div>
                            `;
                        }
                    }
                    
                    // Show errors if any
                    if (data.errors && data.errors.length > 0) {
                        console.warn('Wallet errors:', data.errors);
                        showNotification('Wallet connection issues: ' + data.errors.join(', '), 'warning');
                    }
                    
                    // Update trades table
                    updateTradesTable(data.recent_trades || []);
                    
                    // Update trading status
                    updateTradingStatus();
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('connectionStatus').textContent = 'Disconnected';
                    showNotification('Connection error: ' + error.message, 'danger');
                });
        }

        function updateTradesTable(trades) {
            const tradesBody = document.getElementById('tradesBody');
            if (trades.length > 0) {
                tradesBody.innerHTML = '';
                trades.slice(-5).reverse().forEach(trade => {
                    const row = tradesBody.insertRow();
                    row.innerHTML = `
                        <td><code>${trade.id}</code></td>
                        <td>${new Date(trade.timestamp).toLocaleTimeString()}</td>
                        <td>
                            <span class="badge bg-info">
                                <i class="fas fa-exchange-alt me-1"></i>${trade.direction}
                            </span>
                        </td>
                        <td><strong>$${trade.amount}</strong></td>
                        <td class="${trade.actual_profit > 0 ? 'profit-positive' : 'profit-negative'}">
                            <i class="fas fa-${trade.actual_profit > 0 ? 'arrow-up' : 'arrow-down'} me-1"></i>
                            $${trade.actual_profit.toFixed(2)}
                        </td>
                        <td><span class="badge badge-success">Success</span></td>
                    `;
                });
            }
        }

        function startBot() {
            fetch('/api/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('🚀 ' + data.message, 'success');
                        updateTradingStatus();
                    } else {
                        showNotification('❌ ' + (data.message || 'Unknown error'), 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('❌ Error starting trading agent', 'danger');
                });
        }

        function stopBot() {
            fetch('/api/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('⏹️ ' + data.message, 'warning');
                        updateTradingStatus();
                    } else {
                        showNotification('❌ ' + (data.message || 'Unknown error'), 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('❌ Error stopping trading agent', 'danger');
                });
        }

        function updateTradingStatus() {
            fetch('/api/trading/status')
                .then(response => response.json())
                .then(data => {
                    if (data.active) {
                        document.getElementById('botStatus').textContent = '🚀 Trading Active';
                        document.querySelector('.status-indicator').className = 'status-indicator status-running';
                    } else {
                        document.getElementById('botStatus').textContent = '⏹️ Stopped';
                        document.querySelector('.status-indicator').className = 'status-indicator status-stopped';
                    }
                    
                    // Update trading stats if available
                    if (data.total_trades !== undefined) {
                        document.getElementById('totalTrades').textContent = data.total_trades;
                    }
                    if (data.total_profit !== undefined) {
                        document.getElementById('totalProfit').textContent = '$' + data.total_profit.toFixed(2);
                    }
                })
                .catch(error => {
                    console.error('Error updating trading status:', error);
                });
        }
                    if (data.success) {
                        showNotification('Bot stopped successfully!', 'warning');
                    } else {
                        showNotification('Error: ' + (data.error || 'Unknown error'), 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error stopping bot', 'danger');
                });
        }

        function showNotification(message, type) {
            // Create toast notification
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} position-fixed`;
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            toast.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check' : type === 'warning' ? 'exclamation' : 'times'} me-2"></i>
                ${message}
            `;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        function initializeWallets() {
            showNotification('Initializing wallet connections...', 'info');
            fetch('/api/initialize', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ Wallet connections initialized!', 'success');
                        updateDashboard(); // Refresh data
                    } else {
                        showNotification('❌ Wallet initialization failed: ' + data.error, 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('❌ Error initializing wallets', 'danger');
                });
        }

        // Update every 5 seconds (less frequent for real API calls)
        setInterval(updateDashboard, 5000);
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            showNotification('🚀 Dashboard loading...', 'info');
            initializeWallets();
            updateDashboard();
        });
        
        // Initialize connection status
        document.getElementById('connectionStatus').textContent = 'Connected';
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/status')
def get_status():
    """Get current bot status with real wallet data"""
    try:
        # Run async wallet data collection in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get real portfolio data
        portfolio_data = loop.run_until_complete(wallet_manager.get_comprehensive_portfolio())
        
        # Get real prices
        sol_price = loop.run_until_complete(wallet_manager.get_token_price("SOL"))
        eth_price = loop.run_until_complete(wallet_manager.get_token_price("ETH"))
        
        loop.close()
        
        # Calculate trading data
        total_trades = 0
        total_profit = 0
        
        # Extract Solana data
        solana_balance = 0
        if portfolio_data.get("solana"):
            solana_balance = portfolio_data["solana"].get("sol_balance", 0)
        
        # Extract Ethereum data  
        ethereum_balance = 0
        if portfolio_data.get("ethereum"):
            ethereum_balance = portfolio_data["ethereum"].get("eth_balance", 0)
        
        response_data = {
            "running": True,
            "trades_executed": total_trades,
            "total_profit": total_profit,
            "portfolio_value": portfolio_data.get("total_usd_value", 0),
            "price_data": {
                "solana": {
                    "price": sol_price,
                    "balance": solana_balance,
                    "timestamp": datetime.now().isoformat(),
                    "exchange": "live_data"
                },
                "ethereum": {
                    "price": eth_price,
                    "balance": ethereum_balance, 
                    "timestamp": datetime.now().isoformat(),
                    "exchange": "live_data"
                }
            },
            "wallet_data": portfolio_data,
            "recent_trades": [],
            "errors": portfolio_data.get("errors", [])
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "running": False,
            "error": str(e),
            "trades_executed": 0,
            "total_profit": 0,
            "price_data": {
                "solana": {"price": 0, "timestamp": datetime.now().isoformat()},
                "ethereum": {"price": 0, "timestamp": datetime.now().isoformat()}
            }
        })

@app.route('/api/wallets')
def get_wallet_details():
    """Get detailed wallet information"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        wallet_data = loop.run_until_complete(wallet_manager.get_comprehensive_portfolio())
        loop.close()
        
        return jsonify(wallet_data)
        
    except Exception as e:
        logger.error(f"Error getting wallet details: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/initialize', methods=['POST'])
def initialize_wallets():
    """Initialize wallet connections"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(wallet_manager.initialize_clients())
        loop.close()
        
        return jsonify({"success": True, "message": "Wallet clients initialized"})
        
    except Exception as e:
        logger.error(f"Error initializing wallets: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/start', methods=['POST'])
def start_trading():
    """Start automated trading"""
    try:
        success = asyncio.run(trading_execution_agent.start_automated_trading())
        if success:
            return jsonify({"success": True, "message": "🚀 Automated trading started successfully"})
        else:
            return jsonify({"success": False, "message": "Trading is already active"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to start trading: {str(e)}"})

@app.route('/api/stop', methods=['POST']) 
def stop_trading():
    """Stop automated trading"""
    try:
        success = trading_execution_agent.stop_automated_trading()
        if success:
            return jsonify({"success": True, "message": "⏹️ Automated trading stopped successfully"})
        else:
            return jsonify({"success": False, "message": "Trading was not active"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to stop trading: {str(e)}"})

@app.route('/api/trading/status')
def get_trading_status():
    """Get trading status and statistics"""
    try:
        status = trading_execution_agent.get_trading_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": f"Failed to get trading status: {str(e)}"})

@app.route('/api/trading/history')
def get_trading_history():
    """Get recent trading history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        trades = trading_execution_agent.get_recent_trades(limit)
        return jsonify({"trades": trades})
    except Exception as e:
        return jsonify({"error": f"Failed to get trading history: {str(e)}"})

@app.route('/api/config')
def get_config():
    """Get bot configuration"""
    return jsonify({
        "min_profit_threshold": float(os.getenv('MIN_PROFIT_THRESHOLD', '2.0')),
        "max_trade_amount": float(os.getenv('MAX_TRADE_AMOUNT', '100.0')),
        "gas_cost_estimate": 8.0,
        "monitoring_interval": 10,
        "supported_chains": ["solana", "ethereum"],
        "supported_dexes": ["raydium", "uniswap_v3"],
        "trading_features": {
            "real_wallet_integration": True,
            "automated_execution": True,
            "risk_management": True,
            "profit_tracking": True
        }
    })

if __name__ == '__main__':
    print("🚀 ENHANCED CROSS-CHAIN ARBITRAGE DASHBOARD")
    print("=" * 60)
    print("📊 Real Wallet Integration Features:")
    print("  ✅ Solana wallet portfolio tracking")
    print("  ✅ MetaMask/Ethereum wallet integration") 
    print("  ✅ Binance account portfolio monitoring")
    print("  ✅ Real-time price feeds from multiple exchanges")
    print("  ✅ Live token balance updates")
    print("  ✅ Cross-chain portfolio aggregation")
    print("=" * 60)
    print("🔧 Configuration:")
    print("  1. Copy .env.template to .env")
    print("  2. Add your wallet addresses and API keys")
    print("  3. Install dependencies: pip install -r requirements.txt")
    print("=" * 60)
    print("🌐 Dashboard URL: http://localhost:5000")
    print("📱 Mobile-friendly responsive design")
    print("🎨 Dark theme with real-time updates")
    print("=" * 60)
    
    # Initialize wallet manager
    try:
        print("🔄 Initializing wallet connections...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(wallet_manager.initialize_clients())
        loop.close()
        print("✅ Wallet manager initialized")
    except Exception as e:
        print(f"⚠️ Wallet initialization warning: {e}")
        print("💡 Configure .env file for full functionality")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
