# JuliaOS Arbitrage Agent Test Script (PowerShell)
# This script tests the Groq-powered cross-chain arbitrage agent

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$URL_BASE = "http://localhost:8052/api/v1"

Write-Host "=== JuliaOS Arbitrage Agent Test ===" -ForegroundColor Green
Write-Host ""

Write-Host "1. Checking current agents:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/" -Method GET
    if ($response) {
        $response | ConvertTo-Json -Depth 10
    } else {
        Write-Host "No agents found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error checking agents: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "2. Testing arbitrage agent if available:" -ForegroundColor Yellow
try {
    # First check if basic-groq-agent exists
    $agent = Invoke-RestMethod -Uri "$URL_BASE/agents/basic-groq-agent" -Method GET
    Write-Host "Found agent: basic-groq-agent" -ForegroundColor Green
    
    # Test basic functionality
    Write-Host "Testing basic Groq agent functionality..." -ForegroundColor Cyan
    $testData = @{
        text = "Analyze arbitrage opportunities between Ethereum and Solana for SOL/USDC trading pairs. Look for price differences and calculate potential profits."
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$URL_BASE/agents/basic-groq-agent/webhook" -Method POST -Body $testData -ContentType "application/json"
        Write-Host "Agent Response:" -ForegroundColor White
        Write-Host ($response | ConvertTo-Json -Depth 5) -ForegroundColor White
    } catch {
        Write-Host "Error in agent test: $_" -ForegroundColor Red
        Write-Host "Trying alternative test with simple-working-agent..." -ForegroundColor Yellow
        try {
            $testData2 = @{ text = "Hello, can you help with cryptocurrency analysis?" } | ConvertTo-Json
            $response = Invoke-RestMethod -Uri "$URL_BASE/agents/simple-working-agent/webhook" -Method POST -Body $testData2 -ContentType "application/json"
            Write-Host "Simple Agent Response:" -ForegroundColor White
            Write-Host ($response | ConvertTo-Json -Depth 5) -ForegroundColor White
        } catch {
            Write-Host "Error with simple agent too: $_" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "groq-arbitrage-agent not found, trying groq-arbitrage-complete-v2..." -ForegroundColor Yellow
    try {
        $agent = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-arbitrage-complete-v2" -Method GET
        Write-Host "Found agent: groq-arbitrage-complete-v2" -ForegroundColor Green
        
        # Test with the other agent
        $arbitrageData = @{
            prompt = "Find cross-chain arbitrage opportunities for SOL/USDC between different networks"
            task_type = "analysis"
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-arbitrage-complete-v2/webhook" -Method POST -Body $arbitrageData -ContentType "application/json"
            Write-Host "Arbitrage Analysis Response:" -ForegroundColor White
            Write-Host $response.output -ForegroundColor White
        } catch {
            Write-Host "Error in arbitrage test: $_" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "No arbitrage agents found. Creating one..." -ForegroundColor Yellow
        
        # Create the arbitrage agent
        try {
            $agentData = Get-Content "data\create-groq-agent.json" -Raw
            $response = Invoke-RestMethod -Uri "$URL_BASE/agents/" -Method POST -Body $agentData -ContentType "application/json"
            Write-Host "Agent created successfully!" -ForegroundColor Green
            Write-Host "Agent ID: $($response.id)" -ForegroundColor Green
            
            # Start the agent
            $runAgentData = '{"state": "RUNNING"}'
            $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-arbitrage-agent" -Method PUT -Body $runAgentData -ContentType "application/json"
            Write-Host "Agent started successfully!" -ForegroundColor Green
            
        } catch {
            Write-Host "Error creating agent: $_" -ForegroundColor Red
            Write-Host "Response details: $($_.Exception.Response.StatusCode) - $($_.Exception.Response.StatusDescription)" -ForegroundColor Red
        }
    }
}
Write-Host ""

Write-Host "3. Testing individual tools (if agent exists):" -ForegroundColor Yellow

# Test price fetching
Write-Host "Test A: Price Fetching" -ForegroundColor Cyan
$priceData = @{
    prompt = "Get current SOL price from Jupiter DEX on Solana and compare with Ethereum DEX prices"
    task_type = "price_analysis"
    action = "fetch_prices"
    token = "SOL"
    networks = @("solana", "ethereum")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-arbitrage-agent/webhook" -Method POST -Body $priceData -ContentType "application/json"
    Write-Host "Price Analysis Response:" -ForegroundColor White
    Write-Host $response.output -ForegroundColor White
} catch {
    Write-Host "Error in price test: $_" -ForegroundColor Red
}
Write-Host ""

# Test trade simulation
Write-Host "Test B: Trade Simulation" -ForegroundColor Cyan
$tradeData = @{
    prompt = "Simulate a cross-chain arbitrage trade: buy 10 SOL on Ethereum and sell on Solana. Calculate gas fees and profit potential."
    task_type = "trade_simulation"
    action = "simulate_trade"
    amount = 10
    token = "SOL"
    buy_network = "ethereum"
    sell_network = "solana"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-arbitrage-agent/webhook" -Method POST -Body $tradeData -ContentType "application/json"
    Write-Host "Trade Simulation Response:" -ForegroundColor White
    Write-Host $response.output -ForegroundColor White
} catch {
    Write-Host "Error in trade simulation test: $_" -ForegroundColor Red
}
Write-Host ""

# Test bridge analysis
Write-Host "Test C: Bridge Analysis" -ForegroundColor Cyan
$bridgeData = @{
    prompt = "Analyze bridge options for transferring SOL from Ethereum to Solana. Compare Wormhole, LayerZero costs and timing."
    task_type = "bridge_analysis"
    action = "analyze_bridges"
    token = "SOL"
    from_network = "ethereum"
    to_network = "solana"
    amount = 10
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$URL_BASE/agents/groq-arbitrage-agent/webhook" -Method POST -Body $bridgeData -ContentType "application/json"
    Write-Host "Bridge Analysis Response:" -ForegroundColor White
    Write-Host $response.output -ForegroundColor White
} catch {
    Write-Host "Error in bridge analysis test: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Test Complete ===" -ForegroundColor Green
Write-Host "Your arbitrage agent testing is complete! Check the responses above for arbitrage opportunities." -ForegroundColor Green
