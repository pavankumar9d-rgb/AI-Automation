<#
.SYNOPSIS
    Instagram AI Automation - Daily Snapshot Collection
.DESCRIPTION
    Collects daily Instagram metrics and saves historical snapshots for trend analysis.
    Run via Windows Task Scheduler at 06:00 daily.
.NOTES
    Requires: Instagram MCP installed and configured
    Author: Instagram AI Automation System
#>

param(
    [string]$Workspace = "C:\Users\saipa\Instagram-AI-Automation",
    [string]$AccountName = "main",
    [int]$MediaLimit = 20
)

# Setup
$Date = Get-Date -Format "yyyy-MM-dd"
$Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
$DailyDir = Join-Path $Workspace "analytics\daily"

# Ensure directory exists
if (-not (Test-Path $DailyDir)) {
    New-Item -ItemType Directory -Path $DailyDir -Force | Out-Null
}

Write-Host "[$Timestamp] Starting daily snapshot collection..." -ForegroundColor Green

# Change to workspace
Set-Location $Workspace

# Function to run MCP command and save JSON
function Invoke-McpCommand {
    param(
        [string]$Tool,
        [string]$ArgsJson,
        [string]$OutputFile
    )

    $cmd = "instagram-mcp call $Tool --args '$ArgsJson' --agent"
    try {
        $result = Invoke-Expression $cmd
        $result | Out-File -FilePath $OutputFile -Encoding utf8
        Write-Host "  ✓ Saved: $OutputFile" -ForegroundColor Cyan
        return $true
    }
    catch {
        Write-Host "  ✗ Failed: $Tool`n    Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 1. Get account list
$accountsFile = Join-Path $DailyDir "$Date-accounts.json"
Invoke-McpCommand -Tool "list_accounts" -ArgsJson "{}" -OutputFile $accountsFile

# 2. Account insights (daily)
$insightsFile = Join-Path $DailyDir "$Date-$AccountName-account-insights.json"
$insightsArgs = @"
{
    "account": "$AccountName",
    "period": "day"
}
"@
Invoke-McpCommand -Tool "get_account_insights" -ArgsJson $insightsArgs -OutputFile $insightsFile

# 3. Recent media
$mediaFile = Join-Path $DailyDir "$Date-$AccountName-media.json"
$mediaArgs = @"
{
    "account": "$AccountName",
    "limit": $MediaLimit
}
"@
Invoke-McpCommand -Tool "get_media" -ArgsJson $mediaArgs -OutputFile $mediaFile

# 4. Growth history
$growthFile = Join-Path $DailyDir "$Date-$AccountName-growth.json"
Invoke-McpCommand -Tool "growth_history" -ArgsJson @"
{
    "account": "$AccountName"
}
"@ -OutputFile $growthFile

# 5. Post movement
$movementFile = Join-Path $DailyDir "$Date-$AccountName-post-movement.json"
Invoke-McpCommand -Tool "post_movement" -ArgsJson @"
{
    "account": "$AccountName"
}
"@ -OutputFile $movementFile

# 6. Publishing limit
$quotaFile = Join-Path $DailyDir "$Date-$AccountName-publishing-limit.json"
Invoke-McpCommand -Tool "get_publishing_limit" -ArgsJson @"
{
    "account": "$AccountName"
}
"@ -OutputFile $quotaFile

# 7. Generate summary markdown
$summaryFile = Join-Path $DailyDir "$Date-$AccountName-summary.md"
$summary = @"
# Daily Snapshot: $Date

## Account: @$AccountName

### Collection Time
$Timestamp

### Files Generated
- Account List: `$Date-accounts.json`
- Account Insights: `$Date-$AccountName-account-insights.json`
- Recent Media: `$Date-$AccountName-media.json`
- Growth History: `$Date-$AccountName-growth.json`
- Post Movement: `$Date-$AccountName-post-movement.json`
- Publishing Limit: `$Date-$AccountName-publishing-limit.json`

### Next Steps
1. Parse insights for key metrics
2. Update growth-history.csv
3. Check for anomalies
4. Identify top performing content

---
*Generated automatically by Instagram AI Automation*
"@

$summary | Out-File -FilePath $summaryFile -Encoding utf8
Write-Host "  ✓ Saved: $summaryFile" -ForegroundColor Cyan

# 8. Append to growth history CSV (placeholder - requires parsing actual data)
$csvFile = Join-Path $DailyDir "growth-history.csv"
if (-not (Test-Path $csvFile)) {
    "date,account,followers,reach,impressions,profile_views,website_clicks" | Out-File -FilePath $csvFile -Encoding utf8
}
# Note: Actual CSV append requires parsing JSON files
# This is a placeholder - implement parsing based on your needs
"$Date,$AccountName,,,,," | Out-File -FilePath $csvFile -Encoding utf8 -Append

Write-Host "[$Timestamp] Daily snapshot complete!" -ForegroundColor Green
Write-Host "Files saved to: $DailyDir\$Date-*" -ForegroundColor Cyan