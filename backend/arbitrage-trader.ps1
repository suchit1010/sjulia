# ===============================================
# 🚀 REAL-TIME ARBITRAGE MONITOR & TRADER
# ===============================================
# Continuous monitoring with trading execution preparation

param(
    [switch]$Monitor,
    [switch]$Trade,
    [decimal]$MinSpread = 0.2,
    [int]$RefreshSeconds = 30
)

Write-Host "REAL-TIME ARBITRAGE MONITOR" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "===========================" -ForegroundColor Green

# Load environment variables
$envPath = ".\.env"
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Enhanced price fetching with timestamps
function Get-RealTimePrices {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prices = @{
        Timestamp = $timestamp
        Data = @{}
    }
    
    # Binance (fastest)
    try {
        $btcBin = [double](Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").price
        $ethBin = [double](Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT").price
        $solBin = [double](Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT").price
        
        $prices.Data.Binance = @{ BTC = $btcBin; ETH = $ethBin; SOL = $solBin }
        Write-Host "[$timestamp] Binance: BTC=$btcBin ETH=$ethBin SOL=$solBin" -ForegroundColor Green
    } catch {
        Write-Host "[$timestamp] Binance failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # CoinGecko 
    try {
        $cgData = Invoke-RestMethod -Uri "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd"
        $prices.Data.CoinGecko = @{
            BTC = [double]$cgData.bitcoin.usd
            ETH = [double]$cgData.ethereum.usd
            SOL = [double]$cgData.solana.usd
        }
        Write-Host "[$timestamp] CoinGecko: BTC=$($cgData.bitcoin.usd) ETH=$($cgData.ethereum.usd) SOL=$($cgData.solana.usd)" -ForegroundColor Cyan
    } catch {
        Write-Host "[$timestamp] CoinGecko failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Coinbase
    try {
        $btcCB = [double](Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=BTC").data.rates.USD
        $ethCB = [double](Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=ETH").data.rates.USD  
        $solCB = [double](Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=SOL").data.rates.USD
        
        $prices.Data.Coinbase = @{ BTC = $btcCB; ETH = $ethCB; SOL = $solCB }
        Write-Host "[$timestamp] Coinbase: BTC=$btcCB ETH=$ethCB SOL=$solCB" -ForegroundColor Yellow
    } catch {
        Write-Host "[$timestamp] Coinbase failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $prices
}

# Advanced arbitrage analysis
function Find-ProfitableArbitrage($priceData, $minSpread) {
    $opportunities = @()
    $timestamp = $priceData.Timestamp
    
    foreach ($token in @("BTC", "ETH", "SOL")) {
        $tokenPrices = @{}
        foreach ($exchange in $priceData.Data.Keys) {
            if ($priceData.Data[$exchange][$token]) {
                $tokenPrices[$exchange] = $priceData.Data[$exchange][$token]
            }
        }
        
        if ($tokenPrices.Count -ge 2) {
            $exchanges = $tokenPrices.Keys | Sort-Object
            for ($i = 0; $i -lt $exchanges.Count; $i++) {
                for ($j = $i + 1; $j -lt $exchanges.Count; $j++) {
                    $exchange1 = $exchanges[$i]
                    $exchange2 = $exchanges[$j]
                    
                    $price1 = $tokenPrices[$exchange1]
                    $price2 = $tokenPrices[$exchange2]
                    
                    $spread = [Math]::Abs($price1 - $price2)
                    $spreadPercent = ($spread / [Math]::Min($price1, $price2)) * 100
                    
                    if ($spreadPercent -ge $minSpread) {
                        $buyExchange = if ($price1 -lt $price2) { $exchange1 } else { $exchange2 }
                        $sellExchange = if ($price1 -lt $price2) { $exchange2 } else { $exchange1 }
                        $buyPrice = [Math]::Min($price1, $price2)
                        $sellPrice = [Math]::Max($price1, $price2)
                        
                        # Calculate net profit after fees (estimated 0.3% total)
                        $grossProfit = $spread
                        $fees = ($buyPrice + $sellPrice) * 0.003  # 0.3% total fees
                        $netProfit = $grossProfit - $fees
                        
                        $opportunity = @{
                            Timestamp = $timestamp
                            Token = $token
                            BuyFrom = $buyExchange
                            SellTo = $sellExchange
                            BuyPrice = $buyPrice
                            SellPrice = $sellPrice
                            Spread = $spread
                            SpreadPercent = $spreadPercent
                            GrossProfit = $grossProfit
                            EstimatedFees = $fees
                            NetProfit = $netProfit
                            Profitable = $netProfit -gt 0
                        }
                        
                        $opportunities += $opportunity
                    }
                }
            }
        }
    }
    
    return $opportunities | Sort-Object SpreadPercent -Descending
}

# Trading execution preparation (simulation mode)
function Show-TradingStrategy($opportunity) {
    $color = if ($opportunity.NetProfit -gt 0) { "Green" } else { "Red" }
    
    Write-Host "`n🎯 TRADING OPPORTUNITY DETECTED:" -ForegroundColor Magenta -BackgroundColor DarkMagenta
    Write-Host "================================" -ForegroundColor Magenta
    Write-Host "> Token: $($opportunity.Token)" -ForegroundColor White
    Write-Host "> Time: $($opportunity.Timestamp)" -ForegroundColor Gray
    Write-Host "> Strategy: Buy from $($opportunity.BuyFrom) at $($opportunity.BuyPrice)" -ForegroundColor Green
    Write-Host ">          Sell to $($opportunity.SellTo) at $($opportunity.SellPrice)" -ForegroundColor Red
    Write-Host "> Spread: $($opportunity.SpreadPercent.ToString('F4'))%" -ForegroundColor Yellow
    Write-Host "> Gross Profit: $($opportunity.GrossProfit.ToString('F2')) USD per unit" -ForegroundColor Cyan
    Write-Host "> Estimated Fees: $($opportunity.EstimatedFees.ToString('F2')) USD per unit" -ForegroundColor Orange
    Write-Host "> NET PROFIT: $($opportunity.NetProfit.ToString('F2')) USD per unit" -ForegroundColor $color
    
    if ($opportunity.Profitable) {
        Write-Host "> STATUS: PROFITABLE - READY TO EXECUTE" -ForegroundColor Green -BackgroundColor DarkGreen
        
        # Trading size recommendations
        $smallTrade = 0.1
        $mediumTrade = 1.0
        $largeTrade = 5.0
        
        Write-Host "`n💰 POSITION SIZING:" -ForegroundColor Yellow
        Write-Host "  Small ($smallTrade units): $($opportunity.NetProfit * $smallTrade | ForEach-Object {'{0:F2}' -f $_}) USD profit" -ForegroundColor White
        Write-Host "  Medium ($mediumTrade units): $($opportunity.NetProfit * $mediumTrade | ForEach-Object {'{0:F2}' -f $_}) USD profit" -ForegroundColor White  
        Write-Host "  Large ($largeTrade units): $($opportunity.NetProfit * $largeTrade | ForEach-Object {'{0:F2}' -f $_}) USD profit" -ForegroundColor White
        
        Write-Host "`n⚡ EXECUTION CHECKLIST:" -ForegroundColor Blue
        Write-Host "  1. Verify order book liquidity on both exchanges" -ForegroundColor White
        Write-Host "  2. Check current network fees (gas/transaction costs)" -ForegroundColor White
        Write-Host "  3. Ensure sufficient balance on buy exchange" -ForegroundColor White
        Write-Host "  4. Execute buy order first, then immediate sell" -ForegroundColor White
        Write-Host "  5. Monitor execution time (keep under 30 seconds)" -ForegroundColor White
        
        return $true
    } else {
        Write-Host "> STATUS: NOT PROFITABLE AFTER FEES" -ForegroundColor Red
        return $false
    }
}

# Main monitoring loop
function Start-ArbitrageMonitoring($minSpread, $refreshSeconds) {
    Write-Host "`n🔍 STARTING CONTINUOUS ARBITRAGE MONITORING" -ForegroundColor Cyan
    Write-Host "Min Profitable Spread: $minSpread%" -ForegroundColor White
    Write-Host "Refresh Interval: $refreshSeconds seconds" -ForegroundColor White
    Write-Host "Press Ctrl+C to stop monitoring`n" -ForegroundColor Gray
    
    $iteration = 1
    $totalOpportunities = 0
    $profitableOpportunities = 0
    
    while ($true) {
        try {
            Write-Host "[$iteration] ==================== SCAN $iteration ====================" -ForegroundColor Blue
            
            $priceData = Get-RealTimePrices
            $opportunities = Find-ProfitableArbitrage $priceData $minSpread
            
            if ($opportunities.Count -eq 0) {
                Write-Host "No profitable opportunities found (spreads below $minSpread%)" -ForegroundColor Gray
            } else {
                $totalOpportunities += $opportunities.Count
                
                foreach ($opp in $opportunities) {
                    if ($opp.Profitable) {
                        $profitableOpportunities++
                        $executed = Show-TradingStrategy $opp
                        
                        # In real trading mode, this is where you'd execute
                        if ($Trade -and $executed) {
                            Write-Host "`n🚨 TRADE MODE: Would execute trade here!" -ForegroundColor Red -BackgroundColor Yellow
                            Write-Host "   (Connect to exchange APIs for actual execution)" -ForegroundColor Yellow
                        }
                    }
                }
            }
            
            Write-Host "`n📊 SESSION STATS:" -ForegroundColor Magenta
            Write-Host "   Total Scans: $iteration" -ForegroundColor White
            Write-Host "   Opportunities Found: $totalOpportunities" -ForegroundColor White  
            Write-Host "   Profitable Trades: $profitableOpportunities" -ForegroundColor Green
            Write-Host "   Success Rate: $(if($totalOpportunities -gt 0){[Math]::Round(($profitableOpportunities/$totalOpportunities)*100,1)}else{0})%" -ForegroundColor Cyan
            
            $iteration++
            Start-Sleep -Seconds $refreshSeconds
            
        } catch {
            Write-Host "Error in monitoring loop: $($_.Exception.Message)" -ForegroundColor Red
            Start-Sleep -Seconds 5
        }
    }
}

# Command line interface
if ($Monitor) {
    Start-ArbitrageMonitoring $MinSpread $RefreshSeconds
} else {
    Write-Host "`n🎯 SINGLE SCAN MODE" -ForegroundColor Yellow
    Write-Host "==================" -ForegroundColor Yellow
    
    $priceData = Get-RealTimePrices
    $opportunities = Find-ProfitableArbitrage $priceData $MinSpread
    
    if ($opportunities.Count -eq 0) {
        Write-Host "`nNo profitable opportunities found (minimum spread: $MinSpread%)" -ForegroundColor Gray
        Write-Host "Current market conditions show tight spreads - try lowering -MinSpread parameter" -ForegroundColor White
    } else {
        foreach ($opp in $opportunities) {
            Show-TradingStrategy $opp
        }
    }
    
    Write-Host "`n🚀 USAGE OPTIONS:" -ForegroundColor Green
    Write-Host "=================" -ForegroundColor Green
    Write-Host "Single scan:          .\arbitrage-trader.ps1" -ForegroundColor White
    Write-Host "Continuous monitor:   .\arbitrage-trader.ps1 -Monitor" -ForegroundColor White
    Write-Host "Lower threshold:      .\arbitrage-trader.ps1 -MinSpread 0.1" -ForegroundColor White
    Write-Host "Fast refresh:         .\arbitrage-trader.ps1 -Monitor -RefreshSeconds 10" -ForegroundColor White
    Write-Host "Trading mode:         .\arbitrage-trader.ps1 -Monitor -Trade" -ForegroundColor Red
}
