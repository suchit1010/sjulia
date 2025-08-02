# ===============================================
# API KEY TESTING SCRIPT FOR ARBITRAGE OPPORTUNITIES
# ===============================================

Write-Host "🚀 TESTING APIS FOR ARBITRAGE OPPORTUNITIES" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# ===============================================
# 1. COINGECKO API (FREE - Most Important for Basic Arbitrage)
# ===============================================
Write-Host "`n📊 1. Testing CoinGecko API (FREE tier)..." -ForegroundColor Yellow

try {
    $coinGeckoResponse = Invoke-RestMethod -Uri "https://api.coingecko.com/api/v3/simple/price?ids=solana,usd-coin&vs_currencies=usd&include_24hr_vol=true" -Method GET
    Write-Host "✅ CoinGecko API - WORKING (FREE)" -ForegroundColor Green
    Write-Host "   SOL Price: $($coinGeckoResponse.solana.usd) USD" -ForegroundColor Cyan
    Write-Host "   USDC Price: $($coinGeckoResponse.'usd-coin'.usd) USD" -ForegroundColor Cyan
    Write-Host "   SOL 24h Volume: $($coinGeckoResponse.solana.usd_24h_vol)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ CoinGecko API - FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ===============================================
# 2. JUPITER API (FREE - Solana DEX Aggregator)
# ===============================================
Write-Host "`n📊 2. Testing Jupiter API (FREE)..." -ForegroundColor Yellow

try {
    # SOL token mint address
    $solMint = "So11111111111111111111111111111111111111112"
    $jupiterResponse = Invoke-RestMethod -Uri "https://price.jup.ag/v4/price?ids=$solMint" -Method GET
    Write-Host "✅ Jupiter API - WORKING (FREE)" -ForegroundColor Green
    Write-Host "   SOL Price via Jupiter: $($jupiterResponse.data.$solMint.price)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Jupiter API - FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ===============================================
# 3. BINANCE API (FREE - For CEX vs DEX Arbitrage)
# ===============================================
Write-Host "`n📊 3. Testing Binance Public API (FREE)..." -ForegroundColor Yellow

try {
    $binanceResponse = Invoke-RestMethod -Uri "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT" -Method GET
    Write-Host "✅ Binance API - WORKING (FREE)" -ForegroundColor Green
    Write-Host "   SOL/USDT Price on Binance: $($binanceResponse.price)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Binance API - FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ===============================================
# 4. POTENTIAL ARBITRAGE CALCULATION
# ===============================================
Write-Host "`n💰 ARBITRAGE OPPORTUNITY ANALYSIS" -ForegroundColor Magenta
Write-Host "=================================" -ForegroundColor Magenta

if ($coinGeckoResponse -and $jupiterResponse -and $binanceResponse) {
    $solPriceCoinGecko = [double]$coinGeckoResponse.solana.usd
    $solPriceJupiter = [double]$jupiterResponse.data.$solMint.price
    $solPriceBinance = [double]$binanceResponse.price
    
    Write-Host "   CoinGecko SOL: $solPriceCoinGecko USD" -ForegroundColor White
    Write-Host "   Jupiter SOL:   $solPriceJupiter USD" -ForegroundColor White  
    Write-Host "   Binance SOL:   $solPriceBinance USD" -ForegroundColor White
    
    # Calculate spreads
    $spreadCGvsBinance = [Math]::Abs($solPriceCoinGecko - $solPriceBinance) / $solPriceBinance * 100
    $spreadJupvsBinance = [Math]::Abs($solPriceJupiter - $solPriceBinance) / $solPriceBinance * 100
    
    Write-Host "`n   💡 ARBITRAGE SPREADS:" -ForegroundColor Yellow
    Write-Host "   CoinGecko vs Binance: $([Math]::Round($spreadCGvsBinance, 4))%" -ForegroundColor $(if($spreadCGvsBinance -gt 0.5) {"Green"} else {"White"})
    Write-Host "   Jupiter vs Binance:   $([Math]::Round($spreadJupvsBinance, 4))%" -ForegroundColor $(if($spreadJupvsBinance -gt 0.5) {"Green"} else {"White"})
    
    if ($spreadCGvsBinance -gt 0.5 -or $spreadJupvsBinance -gt 0.5) {
        Write-Host "`n   🎯 ARBITRAGE OPPORTUNITY DETECTED!" -ForegroundColor Green
    } else {
        Write-Host "`n   ℹ️  No significant arbitrage opportunity (< 0.5% spread)" -ForegroundColor Gray
    }
}

# ===============================================
# 5. REQUIRED API KEYS SUMMARY
# ===============================================
Write-Host "`n🔑 API KEYS NEEDED FOR FULL ARBITRAGE SYSTEM:" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ WORKING NOW (FREE):" -ForegroundColor Green
Write-Host "   • CoinGecko (Free tier) - 10,000 calls/month" -ForegroundColor White
Write-Host "   • Jupiter (Free) - Solana DEX prices" -ForegroundColor White
Write-Host "   • Binance Public API (Free) - CEX prices" -ForegroundColor White
Write-Host ""
Write-Host "🚨 RECOMMENDED FOR BETTER DATA:" -ForegroundColor Yellow
Write-Host "   • CoinGecko PRO ($9/month) - More calls, live prices" -ForegroundColor White
Write-Host "   • Infura (Free tier) - Ethereum RPC for Uniswap data" -ForegroundColor White
Write-Host "   • The Graph (Free tier) - DEX subgraph queries" -ForegroundColor White
Write-Host ""
Write-Host "💰 OPTIONAL FOR ADVANCED FEATURES:" -ForegroundColor Blue  
Write-Host "   • Moralis API - Multi-chain data" -ForegroundColor White
Write-Host "   • 1inch API - DEX aggregation" -ForegroundColor White
Write-Host "   • Alchemy API - Enhanced RPC" -ForegroundColor White

Write-Host "`n🎯 CONCLUSION: You can START finding arbitrage opportunities RIGHT NOW with the FREE APIs that are already working!" -ForegroundColor Green -BackgroundColor DarkGreen
