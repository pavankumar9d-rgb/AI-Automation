# Weekly Growth Report Workflow

## Overview
Generate comprehensive weekly performance report from daily snapshots.

## Prerequisites
- Daily snapshots available for last 7 days
- Instagram MCP authenticated

## Schedule
Run weekly (recommended: Monday 7 AM)

## Inputs
- `week_start_date` — Monday of reporting week (YYYY-MM-DD)
- `account_name` — Target account

## Outputs
- `analytics/weekly/{{week_start_date}}-report.md` — Full report
- `analytics/weekly/{{week_start_date}}-executive-summary.md` — One-pager
- `analytics/weekly/{{week_start_date}}-charts-data.json` — Data for visualization

---

## Step-by-Step Execution

### Step 1: Aggregate Daily Data

```bash
# Load 7 daily snapshots
for i in {0..6}; do
  DATE=$(date -d "{{week_start_date}} + $i days" +%Y-%m-%d)
  cat analytics/daily/${DATE}-{{account_name}}-snapshot.json
done
```

### Step 2: Calculate Weekly Metrics

| Metric | Calculation |
|--------|-------------|
| Net Follower Growth | End followers - Start followers |
| Avg Daily Reach | Sum(daily reach) / 7 |
| Total Impressions | Sum(daily impressions) |
| Total Engagement | Sum(likes+comments+shares+saves) |
| Avg Engagement Rate | Total Engagement / Total Reach |
| Profile Visits | Sum(daily profile views) |
| Website Clicks | Sum(daily website clicks) |
| Posts Published | Count from media list |
| Best Day | Day with highest reach |
| Worst Day | Day with lowest reach |

### Step 3: Identify Top Content

```bash
# From media insights across week
# Rank by: Reach, Engagement Rate, Shares, Saves
```

### Step 4: Analyze Content Patterns

| Pattern | Analysis |
|---------|----------|
| Best Format | Reel vs Carousel vs Image |
| Best Hook Type | Curiosity, Bold, Transformation, etc. |
| Best Posting Day | Day of week performance |
| Best Posting Time | Hour of day (if data available) |
| Hashtag Performance | Top contributing tags |

### Step 5: Competitor Benchmark (Optional)

```bash
instagram-mcp call compare_accounts --args '{"accounts": ["comp1", "comp2", "comp3", "{{account_name}}"]}'
```

### Step 6: Generate Report

Use template: `config/templates/performance-report.md`

Fill in all sections with weekly data.

### Step 7: Generate Executive Summary

One-page summary with:
- **Headline metric:** Net follower growth
- **Top win:** Best performing post + why
- **Key insight:** One actionable finding
- **Priority:** One thing to do next week
- **Risk:** One thing to watch

### Step 8: Save Chart Data

```json
{
  "week": "{{week_start_date}}",
  "daily_followers": [...],
  "daily_reach": [...],
  "daily_engagement_rate": [...],
  "format_breakdown": {"reels": X, "carousels": Y, "images": Z},
  "top_posts": [...],
  "hashtag_performance": [...]
}
```

---

## Report Template Structure

See `config/templates/performance-report.md` for full template.

Key weekly sections:
1. Executive Summary
2. Follower Growth Analysis
3. Content Performance (Top/Bottom 5)
4. Format Comparison
5. Reel-Specific Metrics
6. Hook Performance
7. Hashtag Performance
8. Audience Engagement (Comments/DMs)
9. Competitor Benchmarking
10. Publishing Efficiency
11. Action Items

---

## Automation (Windows Task Scheduler)

```powershell
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c C:\Users\saipa\Instagram-AI-Automation\automation\scripts\weekly-report.bat'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 07:00
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "IG-Weekly-Report"
```

---

## MCP Commands

```bash
# Weekly account insights
instagram-mcp call get_account_insights --args '{"account": "NAME", "period": "week"}'

# Compare accounts
instagram-mcp call compare_accounts --args '{"accounts": ["A", "B", "C"]}'

# Growth history
instagram-mcp call growth_history --args '{"account": "NAME"}'

# Post movement
instagram-mcp call post_movement --args '{"account": "NAME"}'
```