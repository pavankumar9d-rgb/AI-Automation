@echo off
REM Instagram AI Automation - Daily Snapshot Collection
REM Run via Windows Task Scheduler at 06:00 daily

set WORKSPACE=C:\Users\saipa\Instagram-AI-Automation
set DATE=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
set TIMESTAMP=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%T%time:~0,2%:%time:~3,2%:%time:~6,2%

cd /d %WORKSPACE%

REM Create daily directory if not exists
if not exist analytics\daily mkdir analytics\daily

echo [%TIMESTAMP%] Starting daily snapshot collection...

REM Get account list
instagram-mcp call list_accounts --agent > analytics\daily\%DATE%-accounts.json

REM For each account, collect insights
REM NOTE: Replace 'main' with your actual account name from list_accounts
instagram-mcp call get_account_insights --args "{\"account\": \"main\", \"period\": \"day\"}" --agent > analytics\daily\%DATE%-main-account-insights.json

instagram-mcp call get_media --args "{\"account\": \"main\", \"limit\": 20}" --agent > analytics\daily\%DATE%-main-media.json

instagram-mcp call growth_history --args "{\"account\": \"main\"}" --agent > analytics\daily\%DATE%-main-growth.json

instagram-mcp call post_movement --args "{\"account\": \"main\"}" --agent > analytics\daily\%DATE%-main-post-movement.json

instagram-mcp call get_publishing_limit --args "{\"account\": \"main\"}" --agent > analytics\daily\%DATE%-main-publishing-limit.json

REM Generate summary (requires jq or manual parsing)
echo [%TIMESTAMP%] Daily snapshot complete. Files saved to analytics\daily\%DATE%-*

REM Append to growth history CSV
echo %DATE%,main,^^^^^^^ >> analytics\daily\growth-history.csv

echo [%TIMESTAMP%] Done.