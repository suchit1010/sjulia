# 🎯 ARBITRAGE DEMO - WHAT YOU'LL GET WITH API KEYS
# =================================================

Write-Host "🚀 CURRENT SYSTEM STATUS:" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Test current working APIs
$currentPrices = @{}

# Binance (Working)
try {
    $solBin = [double](Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT").price
    $ethBin = [double](Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT").price
    $currentPrices.Binance = @{ SOL = $solBin; ETH = $ethBin }
    Write-Host "✅ Binance: SOL=$solBin, ETH=$ethBin" -ForegroundColor Green
} catch {
    Write-Host "❌ Binance failed" -ForegroundColor Red
}

# CoinGecko (Working)  
try {
    $cgData = Invoke-RestMethod -Uri "https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd"
    $solCG = [double]$cgData.solana.usd
    $ethCG = [double]$cgData.ethereum.usd
    $currentPrices.CoinGecko = @{ SOL = $solCG; ETH = $ethCG }
    Write-Host "✅ CoinGecko: SOL=$solCG, ETH=$ethCG" -ForegroundColor Green
} catch {
    Write-Host "❌ CoinGecko failed" -ForegroundColor Red
}

# Coinbase (Working)
try {
    $solCB = [double](Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=SOL").data.rates.USD
    $ethCB = [double](Invoke-RestMethod -Uri "https://api.coinbase.com/v2/exchange-rates?currency=ETH").data.rates.USD
    $currentPrices.Coinbase = @{ SOL = $solCB; ETH = $ethCB }
    Write-Host "✅ Coinbase: SOL=$solCB, ETH=$ethCB" -ForegroundColor Green
} catch {
    Write-Host "❌ Coinbase failed" -ForegroundColor Red
}

Write-Host "`n💰 ARBITRAGE OPPORTUNITIES DETECTED:" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta

# Calculate SOL arbitrage
$solPrices = @($currentPrices.Binance.SOL, $currentPrices.CoinGecko.SOL, $currentPrices.Coinbase.SOL)
$solMin = ($solPrices | Measure-Object -Minimum).Minimum
$solMax = ($solPrices | Measure-Object -Maximum).Maximum
$solSpread = ($solMax - $solMin) / $solMin * 100

Write-Host "🪙 SOL Arbitrage Opportunity:" -ForegroundColor Yellow
Write-Host "   Lowest:  $solMin USD" -ForegroundColor Green
Write-Host "   Highest: $solMax USD" -ForegroundColor Red
Write-Host "   Spread:  $([Math]::Round($solSpread, 4))%" -ForegroundColor $(if($solSpread -gt 0.5){"Green"}else{"Gray"})
Write-Host "   Profit:  $([Math]::Round($solMax - $solMin, 2)) USD per SOL" -ForegroundColor Cyan

# Calculate ETH arbitrage
$ethPrices = @($currentPrices.Binance.ETH, $currentPrices.CoinGecko.ETH, $currentPrices.Coinbase.ETH)
$ethMin = ($ethPrices | Measure-Object -Minimum).Minimum
$ethMax = ($ethPrices | Measure-Object -Maximum).Maximum
$ethSpread = ($ethMax - $ethMin) / $ethMin * 100

Write-Host "`n⚡ ETH Arbitrage Opportunity:" -ForegroundColor Yellow
Write-Host "   Lowest:  $ethMin USD" -ForegroundColor Green
Write-Host "   Highest: $ethMax USD" -ForegroundColor Red
Write-Host "   Spread:  $([Math]::Round($ethSpread, 4))%" -ForegroundColor $(if($ethSpread -gt 0.5){"Green"}else{"Gray"})
Write-Host "   Profit:  $([Math]::Round($ethMax - $ethMin, 2)) USD per ETH" -ForegroundColor Cyan

Write-Host "`n🤖 AI ANALYSIS PREVIEW (What you'll get with API keys):" -ForegroundColor Blue
Write-Host "=======================================================" -ForegroundColor Blue

$mockAnalysis = @"
ARBITRAGE ANALYSIS - AI POWERED:

🎯 CURRENT MARKET CONDITIONS:
- SOL spread: $([Math]::Round($solSpread, 4))% - $(if($solSpread -gt 0.5){"PROFITABLE"}else{"Low opportunity"})  
- ETH spread: $([Math]::Round($ethSpread, 4))% - $(if($ethSpread -gt 0.5){"PROFITABLE"}else{"Monitor for better entry"})
- Market volatility: Low (tight spreads indicate efficient pricing)

📊 TRADING RECOMMENDATIONS:
1. SOL Strategy: $(if($solSpread -gt 0.3){"Execute arbitrage - profitable after fees"}else{"Wait for volatility spike"})
2. ETH Strategy: $(if($ethSpread -gt 0.3){"Execute arbitrage - profitable after fees"}else{"Monitor for news-driven opportunities"})
3. Timing: Best opportunities occur during market stress or major news

⚠️ RISK FACTORS:
- Transaction fees: ~0.1-0.3% per trade
- Slippage: ~0.05-0.2% on large orders  
- Execution time: 10-30 seconds cross-exchange
- Network congestion: Monitor gas prices

💡 OPTIMIZATION TIPS:
- Use limit orders to minimize slippage
- Monitor order book depth before execution
- Consider gas fees in profit calculations
- Execute during high volatility periods for better spreads
"@

Write-Host $mockAnalysis -ForegroundColor White

Write-Host "`n🔑 TO GET THIS AI ANALYSIS:" -ForegroundColor Yellow -BackgroundColor DarkRed
Write-Host "===========================" -ForegroundColor Yellow

Write-Host "1. Get XAI API key: https://console.x.ai/ (FREE $25 credit)" -ForegroundColor Cyan
Write-Host "2. OR get OpenAI key: https://platform.openai.com/api-keys ($5 minimum)" -ForegroundColor Cyan
Write-Host "3. Add to .env file or set environment variable" -ForegroundColor Cyan
Write-Host "4. Run: .\multi-ai-arbitrage.ps1" -ForegroundColor Green

Write-Host "`n✅ YOUR NEXT STEPS:" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "1. Choose: XAI (free credits) OR OpenAI (most reliable)" -ForegroundColor White
Write-Host "2. Get API key (takes 2-5 minutes)" -ForegroundColor White
Write-Host "3. Test complete arbitrage system!" -ForegroundColor White

Write-Host "`n🎯 SYSTEM IS READY - JUST NEEDS AI ANALYSIS API KEY!" -ForegroundColor Green -BackgroundColor DarkGreen
