# Daily Analytics Snapshot Workflow

## Overview
Collect daily Instagram metrics and save historical snapshot for trend analysis.

## Prerequisites
- Instagram MCP authenticated
- At least one Facebook Login account configured

## Schedule
Run daily via Windows Task Scheduler or cron (recommended: 6 AM local time)

## Outputs
- `analytics/daily/{{YYYY-MM-DD}}-snapshot.json` — Raw metrics
- `analytics/daily/{{YYYY-MM-DD}}-summary.md` — Human-readable summary
- Updates `analytics/daily/growth-history.csv` — Cumulative follower tracking

---

## Step-by-Step Execution

### Step 1: Get Connected Accounts

```bash
instagram-mcp call list_accounts
```

Save account list for iteration.

---

### Step 2: Collect Account-Level Insights (Per Account)

```bash
# For each account
instagram-mcp call get_account_insights --args '{
  "account": "{{account_name}}",
  "metrics": "followers_count,impressions,reach,profile_views,website_clicks,get_directions_clicks,phone_call_clicks,text_message_clicks,email_contacts",
  "period": "day"
}'
```

**Metrics to capture daily:**
- `followers_count` — Current follower count
- `impressions` — Total content impressions
- `reach` — Unique accounts reached
- `profile_views` — Profile visits
- `website_clicks` — Link in bio clicks
- `get_directions_clicks` — Location clicks
- `phone_call_clicks` — Call button clicks
- `text_message_clicks` — SMS button clicks
- `email_contacts` — Email button clicks

---

### Step 3: Collect Media-Level Insights (Recent Posts)

```bash
# Get recent media (last 7 days)
instagram-mcp call get_media --args '{"account": "{{account_name}}", "limit": 20}'

# For each media item, get insights
instagram-mcp call get_media_insights --args '{
  "media_id": "{{media_id}}",
  "account": "{{account_name}}",
  "metrics": "reach,impressions,engagement,likes,comments,shares,saved,video_views,video_play_retention_graph"
}'
```

---

### Step 4: Collect Growth History

```bash
# This reads local store (built over time)
instagram-mcp call growth_history --args '{"account": "{{account_name}}"}'
```

---

### Step 5: Collect Post Movement (Posts Still Gaining)

```bash
instagram-mcp call post_movement --args '{"account": "{{account_name}}"}'
```

---

### Step 6: Save Raw JSON Snapshot

```json
{
  "date": "{{YYYY-MM-DD}}",
  "timestamp": "{{ISO_TIMESTAMP}}",
  "account": "{{account_name}}",
  "account_insights": { ... },
  "media_insights": [ ... ],
  "growth_history": { ... },
  "post_movement": { ... }
}
```

Save to: `analytics/daily/{{YYYY-MM-DD}}-{{account_name}}-snapshot.json`

---

### Step 7: Generate Human-Readable Summary

```markdown
# Daily Snapshot: {{YYYY-MM-DD}}

## Account: @{{account_handle}}

### Key Metrics
| Metric | Value | vs Yesterday | Trend |
|--------|-------|--------------|-------|
| Followers | {{followers}} | {{followers_diff}} | {{trend}} |
| Reach | {{reach}} | {{reach_diff}} | {{trend}} |
| Impressions | {{impressions}} | {{impr_diff}} | {{trend}} |
| Profile Views | {{profile_views}} | {{pv_diff}} | {{trend}} |
| Website Clicks | {{clicks}} | {{clicks_diff}} | {{trend}} |

### Top Performing Post (24h)
| Post | Format | Reach | Engagement | Eng Rate |
|------|--------|-------|------------|----------|
| {{top_post}} | {{fmt}} | {{reach}} | {{eng}} | {{rate}}% |

### Posts Still Gaining Traction
| Post | Days Old | New Likes (24h) | New Comments | Momentum |
|------|----------|-----------------|--------------|----------|
|      |          |                 |              |          |

### Follower Growth
- **Today:** +{{daily_gain}}
- **7-Day Avg:** +{{weekly_avg}}/day
- **30-Day Trend:** {{trend_description}}

### Notes
{{observations}}
```

Save to: `analytics/daily/{{YYYY-MM-DD}}-{{account_name}}-summary.md`

---

### Step 8: Update Cumulative Growth CSV

```bash
# Append to growth-history.csv
echo "{{YYYY-MM-DD}},{{account_name}},{{followers}},{{reach}},{{impressions}},{{profile_views}},{{website_clicks}}" >> analytics/daily/growth-history.csv
```

**CSV Headers:** `date,account,followers,reach,impressions,profile_views,website_clicks`

---

### Step 9: Check for Anomalies

```bash
# Alert if:
# - Follower drop > 1% (potential bot purge)
# - Reach drop > 50% vs 7-day avg (shadowban/content issue)
# - Zero reach on new post (technical issue)
# - Unusual spike (viral/bot)
```

Log anomalies to: `analytics/daily/anomalies-{{YYYY-MM-DD}}.md`

---

## Automation Setup (Windows Task Scheduler)

```powershell
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c cd C:\Users\saipa\Instagram-AI-Automation && instagram-mcp call get_account_insights ... (full command chain)'
$trigger = New-ScheduledTaskTrigger -Daily -At 06:00
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName "IG-Daily-Analytics" -Description "Collect daily Instagram metrics"
```

---

## MCP Commands Reference

```bash
# Accounts
instagram-mcp call list_accounts

# Account insights (daily)
instagram-mcp call get_account_insights --args '{"account": "NAME", "period": "day"}'

# Account insights (weekly/monthly)
instagram-mcp call get_account_insights --args '{"account": "NAME", "period": "week"}'
instagram-mcp call get_account_insights --args '{"account": "NAME", "period": "month"}'

# Recent media
instagram-mcp call get_media --args '{"account": "NAME", "limit": 20}'

# Media insights
instagram-mcp call get_media_insights --args '{"media_id": "ID", "account": "NAME"}'

# Historical tracking
instagram-mcp call growth_history --args '{"account": "NAME"}'
instagram-mcp call post_movement --args '{"account": "NAME"}'

# Publishing quota
instagram-mcp call get_publishing_limit --args '{"account": "NAME"}'
```

---

## Data Retention

| Data Type | Retention | Location |
|-----------|-----------|----------|
| Raw JSON snapshots | 90 days | `analytics/daily/` |
| Summary markdowns | 1 year | `analytics/daily/` |
| Growth CSV | Permanent | `analytics/daily/growth-history.csv` |
| Anomaly logs | 1 year | `analytics/daily/anomalies-*.md` |

Monthly cleanup script should archive >90 day raw JSON to cold storage.