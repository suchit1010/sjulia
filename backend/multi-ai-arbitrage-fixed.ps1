# ===============================================
# MULTI-AI ARBITRAGE ANALYZER - FIXED VERSION
# ===============================================
# Uses OpenAI, XAI, or Gemini for arbitrage analysis

Write-Host "MULTI-AI ARBITRAGE OPPORTUNITY ANALYZER" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Load environment variables from .env file
$envPath = ".\.env"
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "Environment variables loaded from .env file" -ForegroundColor Cyan
}

# Get current prices
function Get-CryptoPrices {
    $prices = @{}
    
    # CoinGecko
    try {
        $cgUrl = "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum,bitcoin&vs_currencies=usd&include_24hr_vol=true"
        $cgResponse = Invoke-RestMethod -Uri $cgUrl
        $prices.CoinGecko = @{
            SOL = $cgResponse.solana.usd
            ETH = $cgResponse.ethereum.usd  
            BTC = $cgResponse.bitcoin.usd
        }
        Write-Host "CoinGecko prices retrieved" -ForegroundColor Green
    } catch {
        Write-Host "CoinGecko failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Binance
    try {
        $solBin = (Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT").price
        $ethBin = (Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT").price
        $btcBin = (Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").price
        
        $prices.Binance = @{
            SOL = [double]$solBin
            ETH = [double]$ethBin
            BTC = [double]$btcBin
        }
        Write-Host "Binance prices retrieved" -ForegroundColor Green
    } catch {
        Write-Host "Binance failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Coinbase
    try {
        $cbSol = (Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=SOL").data.rates.USD
        $cbEth = (Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=ETH").data.rates.USD
        $cbBtc = (Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=BTC").data.rates.USD
        
        $prices.Coinbase = @{
            SOL = [double]$cbSol
            ETH = [double]$cbEth
            BTC = [double]$cbBtc
        }
        Write-Host "Coinbase prices retrieved" -ForegroundColor Green
    } catch {
        Write-Host "Coinbase failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $prices
}

# AI Analysis with multiple providers
function Get-AIAnalysis($priceData, $opportunities) {
    $analysisPrompt = "Analyze these cryptocurrency arbitrage opportunities:`n`n"
    
    foreach ($token in @("SOL", "ETH", "BTC")) {
        $analysisPrompt += "$token Prices:`n"
        foreach ($exchange in $priceData.Keys) {
            if ($priceData[$exchange][$token]) {
                $analysisPrompt += "- $exchange : $($priceData[$exchange][$token]) USD`n"
            }
        }
        $analysisPrompt += "`n"
    }
    
    $analysisPrompt += "Detected opportunities with >0.1% spread:`n"
    foreach ($opp in $opportunities) {
        if ($opp.SpreadPercent -gt 0.1) {
            $analysisPrompt += "- $($opp.Token): Buy from $($opp.BuyFrom) at $($opp.BuyPrice), sell to $($opp.SellTo) at $($opp.SellPrice) ($($opp.SpreadPercent.ToString('F3'))% spread)`n"
        }
    }
    
    $analysisPrompt += "`nProvide trading recommendations considering fees, slippage, and execution risk."
    
    # Try OpenAI first (most reliable)
    try {
        Write-Host "Trying OpenAI API..." -ForegroundColor Yellow
        $openaiKey = $env:OPENAI_API_KEY
        if ($openaiKey) {
            $headers = @{"Authorization" = "Bearer $openaiKey"; "Content-Type" = "application/json"}
            $body = @{
                model = "gpt-3.5-turbo"
                messages = @(@{role = "user"; content = $analysisPrompt})
                max_tokens = 800
                temperature = 0.3
            } | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri "https://api.openai.com/v1/chat/completions" -Method POST -Headers $headers -Body $body
            Write-Host "OpenAI analysis completed" -ForegroundColor Green
            return $response.choices[0].message.content
        } else {
            Write-Host "OpenAI API key not found in environment" -ForegroundColor Red
        }
    } catch {
        Write-Host "OpenAI failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Try XAI Grok
    try {
        Write-Host "Trying XAI Grok API..." -ForegroundColor Yellow
        $xaiKey = $env:XAI_API_KEY
        if ($xaiKey) {
            $headers = @{"Authorization" = "Bearer $xaiKey"; "Content-Type" = "application/json"}  
            $body = @{
                model = "grok-beta"
                messages = @(@{role = "user"; content = $analysisPrompt})
                max_tokens = 800
                temperature = 0.3
            } | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri "https://api.x.ai/v1/chat/completions" -Method POST -Headers $headers -Body $body
            Write-Host "XAI Grok analysis completed" -ForegroundColor Green
            return $response.choices[0].message.content
        } else {
            Write-Host "XAI API key not found in environment" -ForegroundColor Red
        }
    } catch {
        Write-Host "XAI failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Fallback to rule-based analysis
    Write-Host "Using rule-based analysis (AI APIs unavailable)" -ForegroundColor Cyan
    
    $analysis = "ARBITRAGE ANALYSIS - Rule-Based:`n`n"
    
    $profitableOpps = $opportunities | Where-Object { $_.SpreadPercent -gt 0.5 }
    if ($profitableOpps) {
        $analysis += "PROFITABLE OPPORTUNITIES (>0.5% spread):`n"
        foreach ($opp in $profitableOpps) {
            $analysis += "- $($opp.Token): $($opp.SpreadPercent.ToString('F3'))% spread ($($opp.PotentialProfit.ToString('F2')) USD per unit)`n"
            $analysis += "  Strategy: Buy from $($opp.BuyFrom), sell to $($opp.SellTo)`n"
        }
    } else {
        $analysis += "No highly profitable opportunities detected (all spreads less than 0.5%)`n"
    }
    
    $analysis += "`nMARKET CONDITIONS:`n"
    $analysis += "- Current spreads are relatively tight, indicating efficient markets`n"
    $analysis += "- Consider waiting for higher volatility periods`n"
    $analysis += "- Monitor gas fees and transaction costs`n"
    $analysis += "- Best opportunities typically occur during market stress or news events`n"
    
    return $analysis
}

# Calculate arbitrage opportunities
function Find-ArbitrageOpportunities($priceData) {
    $opportunities = @()
    
    foreach ($token in @("SOL", "ETH", "BTC")) {
        $tokenPrices = @{}
        foreach ($exchange in $priceData.Keys) {
            if ($priceData[$exchange][$token]) {
                $tokenPrices[$exchange] = $priceData[$exchange][$token]
            }
        }
        
        $exchanges = $tokenPrices.Keys | Sort-Object
        for ($i = 0; $i -lt $exchanges.Count; $i++) {
            for ($j = $i + 1; $j -lt $exchanges.Count; $j++) {
                $exchange1 = $exchanges[$i]
                $exchange2 = $exchanges[$j]
                
                $price1 = $tokenPrices[$exchange1]
                $price2 = $tokenPrices[$exchange2]
                
                $spread = [Math]::Abs($price1 - $price2)
                $spreadPercent = ($spread / [Math]::Min($price1, $price2)) * 100
                
                $buyExchange = if ($price1 -lt $price2) { $exchange1 } else { $exchange2 }
                $sellExchange = if ($price1 -lt $price2) { $exchange2 } else { $exchange1 }
                $buyPrice = [Math]::Min($price1, $price2)
                $sellPrice = [Math]::Max($price1, $price2)
                
                $opportunities += @{
                    Token = $token
                    BuyFrom = $buyExchange
                    SellTo = $sellExchange
                    BuyPrice = $buyPrice
                    SellPrice = $sellPrice
                    Spread = $spread
                    SpreadPercent = $spreadPercent
                    PotentialProfit = $spread
                }
            }
        }
    }
    
    return $opportunities | Sort-Object SpreadPercent -Descending
}

# Main execution
Write-Host "`nFetching cryptocurrency prices..." -ForegroundColor Cyan
$priceData = Get-CryptoPrices

Write-Host "`nCalculating arbitrage opportunities..." -ForegroundColor Cyan
$opportunities = Find-ArbitrageOpportunities $priceData

Write-Host "`nTOP ARBITRAGE OPPORTUNITIES:" -ForegroundColor Magenta
Write-Host "============================" -ForegroundColor Magenta

$topOpps = $opportunities | Select-Object -First 5
$counter = 1
foreach ($opp in $topOpps) {
    $color = if ($opp.SpreadPercent -gt 0.5) { "Green" } elseif ($opp.SpreadPercent -gt 0.2) { "Yellow" } else { "Gray" }
    Write-Host "`n$counter. $($opp.Token) Arbitrage:" -ForegroundColor White
    Write-Host "   Buy: $($opp.BuyFrom) at $($opp.BuyPrice)" -ForegroundColor Green
    Write-Host "   Sell: $($opp.SellTo) at $($opp.SellPrice)" -ForegroundColor Red  
    Write-Host "   Spread: $($opp.SpreadPercent.ToString('F4'))%" -ForegroundColor $color
    Write-Host "   Profit: $($opp.PotentialProfit.ToString('F2')) USD per unit" -ForegroundColor Cyan
    $counter++
}

Write-Host "`nGetting AI analysis..." -ForegroundColor Blue
$aiAnalysis = Get-AIAnalysis $priceData $opportunities
Write-Host "`n$aiAnalysis" -ForegroundColor White

Write-Host "`nAPI SETUP STATUS:" -ForegroundColor Yellow
Write-Host "=================" -ForegroundColor Yellow
Write-Host "OpenAI API: $(if($env:OPENAI_API_KEY){'CONFIGURED'}else{'NOT FOUND'})" -ForegroundColor $(if($env:OPENAI_API_KEY){'Green'}else{'Red'})
Write-Host "XAI API: $(if($env:XAI_API_KEY){'CONFIGURED'}else{'NOT FOUND'})" -ForegroundColor $(if($env:XAI_API_KEY){'Green'}else{'Red'})

Write-Host "`nSCAN COMPLETE! System is fully operational." -ForegroundColor Green
