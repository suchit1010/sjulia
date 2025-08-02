# ===============================================
# 🚀 DIRECT ARBITRAGE OPPORTUNITY DETECTOR
# ===============================================
# This script bypasses agent issues and directly finds arbitrage opportunities
# Using the APIs we successfully tested

Write-Host "🎯 REAL-TIME ARBITRAGE OPPORTUNITY SCANNER" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Function to get prices from multiple sources
function Get-ArbitrageData {
    $results = @{}
    
    # 1. CoinGecko Price
    try {
        $cgUrl = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_vol=true"
        $cgResponse = Invoke-RestMethod -Uri $cgUrl
        $results.CoinGecko = @{
            price = [double]$cgResponse.solana.usd
            volume = [double]$cgResponse.solana.usd_24h_vol
            source = "CoinGecko API"
        }
        Write-Host "✅ CoinGecko: $($results.CoinGecko.price) USD" -ForegroundColor Green
    } catch {
        Write-Host "❌ CoinGecko failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # 2. Binance Price  
    try {
        $binanceUrl = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"
        $binanceResponse = Invoke-RestMethod -Uri $binanceUrl
        $results.Binance = @{
            price = [double]$binanceResponse.price
            source = "Binance CEX"
        }
        Write-Host "✅ Binance: $($results.Binance.price) USD" -ForegroundColor Green
    } catch {
        Write-Host "❌ Binance failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # 3. Coinbase Price
    try {
        $coinbaseUrl = "https://api.coinbase.com/v2/exchange-rates?currency=SOL"
        $coinbaseResponse = Invoke-RestMethod -Uri $coinbaseUrl
        $results.Coinbase = @{
            price = [double]$coinbaseResponse.data.rates.USD
            source = "Coinbase CEX"
        }
        Write-Host "✅ Coinbase: $($results.Coinbase.price) USD" -ForegroundColor Green
    } catch {
        Write-Host "❌ Coinbase failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $results
}

# Function to calculate arbitrage opportunities
function Calculate-ArbitrageOpportunities($priceData) {
    $opportunities = @()
    $exchanges = $priceData.Keys | Sort-Object
    
    Write-Host "`n💰 ARBITRAGE ANALYSIS:" -ForegroundColor Yellow
    Write-Host "=====================" -ForegroundColor Yellow
    
    for ($i = 0; $i -lt $exchanges.Count; $i++) {
        for ($j = $i + 1; $j -lt $exchanges.Count; $j++) {
            $exchange1 = $exchanges[$i]
            $exchange2 = $exchanges[$j]
            
            $price1 = $priceData[$exchange1].price
            $price2 = $priceData[$exchange2].price
            
            if ($price1 -and $price2) {
                $spread = [Math]::Abs($price1 - $price2)
                $spreadPercent = ($spread / [Math]::Min($price1, $price2)) * 100
                
                $buyExchange = if ($price1 -lt $price2) { $exchange1 } else { $exchange2 }
                $sellExchange = if ($price1 -lt $price2) { $exchange2 } else { $exchange1 }
                $buyPrice = [Math]::Min($price1, $price2)
                $sellPrice = [Math]::Max($price1, $price2)
                
                $opportunity = @{
                    BuyFrom = $buyExchange
                    SellTo = $sellExchange
                    BuyPrice = $buyPrice  
                    SellPrice = $sellPrice
                    Spread = $spread
                    SpreadPercent = $spreadPercent
                    PotentialProfit = $spread
                }
                
                $opportunities += $opportunity
                
                $color = if ($spreadPercent -gt 0.5) { "Green" } elseif ($spreadPercent -gt 0.2) { "Yellow" } else { "Gray" }
                Write-Host "   $buyExchange → $sellExchange: $([Math]::Round($spreadPercent, 3))% ($([Math]::Round($spread, 2)) USD)" -ForegroundColor $color
            }
        }
    }
    
    return $opportunities | Sort-Object SpreadPercent -Descending
}

# Function to generate AI analysis using Groq
function Get-GroqAnalysis($arbitrageData) {
    try {
        $groqApiKey = "YOUR_GROQ_API_KEY_HERE"
        $headers = @{
            "Authorization" = "Bearer $groqApiKey"
            "Content-Type" = "application/json"
        }
        
        $prompt = "Analyze these real-time SOL arbitrage opportunities:`n"
        foreach ($key in $arbitrageData.Keys) {
            $prompt += "- $key: $($arbitrageData[$key].price) USD`n"
        }
        $prompt += "`nProvide trading strategy recommendations considering fees, slippage, and execution time."
        
        $body = @{
            messages = @(@{
                role = "user"
                content = $prompt
            })
            model = "llama-3.3-70b-versatile"
            max_tokens = 1000
            temperature = 0.3
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri "https://api.groq.com/openai/v1/chat/completions" -Method POST -Headers $headers -Body $body
        
        return $response.choices[0].message.content
    } catch {
        return "Groq AI analysis failed: $($_.Exception.Message)"
    }
}

# Main execution
Write-Host "`n🔍 SCANNING FOR ARBITRAGE OPPORTUNITIES..." -ForegroundColor Cyan

$priceData = Get-ArbitrageData
$opportunities = Calculate-ArbitrageOpportunities $priceData

Write-Host "`n🎯 TOP ARBITRAGE OPPORTUNITIES:" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta

$topOpportunities = $opportunities | Select-Object -First 3
foreach ($opp in $topOpportunities) {
    Write-Host "`n💡 Opportunity #$($topOpportunities.IndexOf($opp) + 1):" -ForegroundColor White
    Write-Host "   Buy from: $($opp.BuyFrom) at $($opp.BuyPrice)" -ForegroundColor Green
    Write-Host "   Sell to: $($opp.SellTo) at $($opp.SellPrice)" -ForegroundColor Red
    Write-Host "   Spread: $([Math]::Round($opp.SpreadPercent, 3))%" -ForegroundColor Yellow
    Write-Host "   Potential Profit: $([Math]::Round($opp.PotentialProfit, 2)) USD per SOL" -ForegroundColor Cyan
    
    if ($opp.SpreadPercent -gt 0.5) {
        Write-Host "   🚨 ACTIONABLE OPPORTUNITY!" -ForegroundColor Green -BackgroundColor DarkGreen
    } elseif ($opp.SpreadPercent -gt 0.2) {
        Write-Host "   ⚠️  Monitor for better entry" -ForegroundColor Yellow
    } else {
        Write-Host "   ℹ️  Too small for profitable trading" -ForegroundColor Gray
    }
}

# Get AI analysis
Write-Host "`n🤖 AI STRATEGY ANALYSIS:" -ForegroundColor Blue
Write-Host "========================" -ForegroundColor Blue
$aiAnalysis = Get-GroqAnalysis $priceData
Write-Host $aiAnalysis -ForegroundColor White

Write-Host "`n✅ SCAN COMPLETE! Monitor these prices continuously for profitable opportunities." -ForegroundColor Green
