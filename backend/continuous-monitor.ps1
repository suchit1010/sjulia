# 🚀 CONTINUOUS ARBITRAGE MONITOR
# Automated trading opportunity detection every 30 seconds

param(
    [int]$IntervalSeconds = 30,
    [decimal]$MinSpread = 0.01,
    [switch]$ShowAll
)

Write-Host "🔥 STARTING CONTINUOUS ARBITRAGE MONITORING 🔥" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Monitoring interval: $IntervalSeconds seconds" -ForegroundColor White
Write-Host "Minimum spread threshold: $MinSpread%" -ForegroundColor White
Write-Host "Press Ctrl+C to stop monitoring`n" -ForegroundColor Gray

$iteration = 1
$bestOpportunities = @()

while ($true) {
    try {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$iteration] ==================== SCAN $iteration - $timestamp ====================" -ForegroundColor Blue
        
        # Run our proven arbitrage script and capture output
        $result = & ".\multi-ai-arbitrage-fixed.ps1" 2>&1
        
        # Parse the output for opportunities
        $lines = $result -split "`n"
        $currentOpportunities = @()
        
        foreach ($line in $lines) {
            if ($line -match "(\w+) Arbitrage:" -and $line -match "Spread: ([\d.]+)%" -and $line -match "Profit: ([\d.]+) USD") {
                $token = $matches[1]
                $spread = [decimal]$matches[2]
                $profit = [decimal]$matches[3]
                
                if ($spread -ge $MinSpread -or $ShowAll) {
                    $opp = @{
                        Timestamp = $timestamp
                        Token = $token
                        Spread = $spread
                        Profit = $profit
                        Line = $line.Trim()
                    }
                    $currentOpportunities += $opp
                }
            }
        }
        
        if ($currentOpportunities.Count -eq 0) {
            Write-Host "No opportunities above $MinSpread% threshold found" -ForegroundColor Gray
        } else {
            Write-Host "🎯 PROFITABLE OPPORTUNITIES DETECTED:" -ForegroundColor Green -BackgroundColor DarkGreen
            
            foreach ($opp in $currentOpportunities | Sort-Object Spread -Descending) {
                Write-Host "   $($opp.Token): $($opp.Spread)% spread = $($opp.Profit) USD profit per unit" -ForegroundColor Yellow
                
                # Track best opportunities
                $bestOpportunities += $opp
                if ($bestOpportunities.Count -gt 50) {
                    $bestOpportunities = $bestOpportunities | Sort-Object Spread -Descending | Select-Object -First 50
                }
                
                # Alert for exceptional opportunities
                if ($opp.Spread -ge 0.1) {
                    Write-Host "   🚨 HIGH PROFIT ALERT: $($opp.Token) showing $($opp.Spread)% spread!" -ForegroundColor Red -BackgroundColor Yellow
                    Write-Host "   💰 Potential profit: $($opp.Profit) USD per unit" -ForegroundColor Green
                }
            }
        }
        
        # Show session statistics
        if ($bestOpportunities.Count -gt 0) {
            $bestEver = $bestOpportunities | Sort-Object Spread -Descending | Select-Object -First 1
            $avgSpread = ($bestOpportunities | Measure-Object -Property Spread -Average).Average
            
            Write-Host "`n📊 SESSION STATS:" -ForegroundColor Magenta
            Write-Host "   Total scans: $iteration" -ForegroundColor White
            Write-Host "   Opportunities found: $($bestOpportunities.Count)" -ForegroundColor White
            Write-Host "   Best spread ever: $($bestEver.Token) at $($bestEver.Spread)% ($($bestEver.Profit) USD)" -ForegroundColor Green
            Write-Host "   Average spread: $($avgSpread.ToString('F4'))%" -ForegroundColor Cyan
        }
        
        Write-Host "Next scan in $IntervalSeconds seconds..." -ForegroundColor Gray
        $iteration++
        Start-Sleep -Seconds $IntervalSeconds
        
    } catch {
        Write-Host "Error in monitoring: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Retrying in 10 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}
