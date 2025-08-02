# 🚀 COMPLETE API KEY SETUP GUIDE - GET STARTED NOW!
# ===============================================

Write-Host "🎯 API KEY SETUP WIZARD" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "=======================" -ForegroundColor Green

Write-Host "`n🔑 STEP 1: GET XAI (GROK) API KEY" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "1. Go to: https://console.x.ai/" -ForegroundColor White
Write-Host "2. Sign up with your Twitter/X account" -ForegroundColor White  
Write-Host "3. Click 'API Keys' in the sidebar" -ForegroundColor White
Write-Host "4. Click 'Create API Key'" -ForegroundColor White
Write-Host "5. Copy the key (starts with 'xai-')" -ForegroundColor Yellow
Write-Host "6. XAI gives you $25 FREE CREDITS to start!" -ForegroundColor Green

Write-Host "`n🔑 STEP 2: GET OPENAI API KEY" -ForegroundColor Cyan  
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "1. Go to: https://platform.openai.com/api-keys" -ForegroundColor White
Write-Host "2. Sign up or log in to your OpenAI account" -ForegroundColor White
Write-Host "3. Click '+ Create new secret key'" -ForegroundColor White
Write-Host "4. Give it a name like 'Arbitrage-Bot'" -ForegroundColor White  
Write-Host "5. Copy the key (starts with 'sk-')" -ForegroundColor Yellow
Write-Host "6. Add $5-20 credit to your account" -ForegroundColor Green

Write-Host "`n🔧 STEP 3: ADD KEYS TO YOUR SYSTEM" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta
Write-Host "Run these commands to add the keys:" -ForegroundColor White

$envPath = "c:\Users\sonis\git\shreos\JuliaOS\backend\.env"
Write-Host "`n# Method 1: Add to .env file" -ForegroundColor Yellow
Write-Host "notepad `"$envPath`"" -ForegroundColor Cyan
Write-Host "`nThen add these lines to the file:" -ForegroundColor White
Write-Host "XAI_API_KEY=xai-your-actual-key-here" -ForegroundColor Green
Write-Host "OPENAI_API_KEY=sk-your-actual-key-here" -ForegroundColor Green

Write-Host "`n# Method 2: Set environment variables directly" -ForegroundColor Yellow  
Write-Host '$env:XAI_API_KEY = "xai-your-actual-key-here"' -ForegroundColor Cyan
Write-Host '$env:OPENAI_API_KEY = "sk-your-actual-key-here"' -ForegroundColor Cyan

Write-Host "`n🧪 STEP 4: TEST YOUR SETUP" -ForegroundColor Blue
Write-Host "==========================" -ForegroundColor Blue
Write-Host "Once you have the keys, run:" -ForegroundColor White
Write-Host ".\multi-ai-arbitrage.ps1" -ForegroundColor Cyan

Write-Host "`n💰 COST BREAKDOWN:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host "XAI Grok:   $25 FREE → ~5000 arbitrage analyses" -ForegroundColor Green
Write-Host "OpenAI:     $5 → ~500 arbitrage analyses" -ForegroundColor Green  
Write-Host "Total Cost: ~$5-25 for thousands of analyses" -ForegroundColor White

Write-Host "`n⚡ QUICK START OPTION:" -ForegroundColor Red -BackgroundColor Yellow
Write-Host "If you want to start IMMEDIATELY, just get the XAI key!" -ForegroundColor White
Write-Host "It's faster to set up and comes with $25 free credits." -ForegroundColor White

Write-Host "`n🎯 WHAT YOU'LL GET:" -ForegroundColor Green
Write-Host "• Real-time arbitrage opportunity detection" -ForegroundColor White
Write-Host "• AI-powered trading strategy recommendations" -ForegroundColor White  
Write-Host "• Multi-exchange price monitoring" -ForegroundColor White
Write-Host "• Profit calculation with fees and slippage" -ForegroundColor White
Write-Host "• Risk assessment and timing analysis" -ForegroundColor White

Write-Host "`n✅ READY TO START? Copy your API keys and let's test!" -ForegroundColor Green -BackgroundColor DarkGreen
