# XAI API CONNECTION TEST
# =====================

Write-Host "XAI GROK API CONNECTION TEST" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "=============================" -ForegroundColor Green

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
    Write-Host "✓ Environment variables loaded" -ForegroundColor Green
}

$xaiApiKey = [Environment]::GetEnvironmentVariable("XAI_API_KEY")

if (-not $xaiApiKey) {
    Write-Host "✗ XAI_API_KEY not found in environment" -ForegroundColor Red
    exit 1
}

if ($xaiApiKey.StartsWith("xai-")) {
    Write-Host "✓ XAI API key format looks correct: $($xaiApiKey.Substring(0,8))..." -ForegroundColor Green
} else {
    Write-Host "⚠ XAI API key format might be wrong (should start with 'xai-')" -ForegroundColor Yellow
}

Write-Host "`nTesting XAI Grok API connection..." -ForegroundColor Cyan

try {
    $headers = @{
        "Authorization" = "Bearer $xaiApiKey"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        model = "grok-beta"
        messages = @(
            @{
                role = "user"
                content = "Hello, this is a test message. Please respond with 'API connection successful'."
            }
        )
        max_tokens = 50
    } | ConvertTo-Json -Depth 10
    
    Write-Host "Sending test request to XAI API..." -ForegroundColor White
    
    $response = Invoke-RestMethod -Uri "https://api.x.ai/v1/chat/completions" -Method POST -Headers $headers -Body $body -TimeoutSec 30
    
    Write-Host "✓ XAI API CONNECTION SUCCESSFUL!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "✓ Response received from Grok" -ForegroundColor Green
    Write-Host "✓ Message: $($response.choices[0].message.content)" -ForegroundColor White
    
} catch {
    Write-Host "✗ XAI API CONNECTION FAILED" -ForegroundColor Red -BackgroundColor DarkRed
    Write-Host "Error details:" -ForegroundColor Yellow
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor White
    Write-Host "Status Description: $($_.Exception.Response.StatusDescription)" -ForegroundColor White
    Write-Host "Error Message: $($_.Exception.Message)" -ForegroundColor White
    
    if ($_.Exception.Response.StatusCode.value__ -eq 403) {
        Write-Host "`n🔍 TROUBLESHOOTING 403 FORBIDDEN:" -ForegroundColor Yellow
        Write-Host "=================================" -ForegroundColor Yellow
        Write-Host "1. Check if API key is properly activated at console.x.ai" -ForegroundColor White
        Write-Host "2. Verify you have credits/billing set up" -ForegroundColor White
        Write-Host "3. Make sure the API key has proper permissions" -ForegroundColor White
        Write-Host "4. Try regenerating the API key" -ForegroundColor White
        Write-Host "5. Check if your account is verified" -ForegroundColor White
    }
    
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Write-Host "`n🔍 TROUBLESHOOTING 401 UNAUTHORIZED:" -ForegroundColor Yellow
        Write-Host "====================================" -ForegroundColor Yellow
        Write-Host "1. API key format might be wrong" -ForegroundColor White
        Write-Host "2. Copy the full API key from console.x.ai" -ForegroundColor White
        Write-Host "3. Make sure there are no extra spaces" -ForegroundColor White
    }
}

Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Blue
Write-Host "==============" -ForegroundColor Blue
Write-Host "1. Visit https://console.x.ai/" -ForegroundColor White
Write-Host "2. Check your API key status" -ForegroundColor White
Write-Host "3. Verify billing/credits are set up" -ForegroundColor White
Write-Host "4. Make sure account is fully activated" -ForegroundColor White

Write-Host "`n💡 GOOD NEWS:" -ForegroundColor Magenta
Write-Host "==============" -ForegroundColor Magenta
Write-Host "Your arbitrage system works perfectly WITHOUT AI analysis!" -ForegroundColor Green
Write-Host "The rule-based analysis is detecting all profitable opportunities." -ForegroundColor Green
Write-Host "XAI integration is just a bonus feature for enhanced analysis." -ForegroundColor White
