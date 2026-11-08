# Publish Reel Workflow

## Overview
Safe, validated Reel publishing workflow with confirmation gates and rollback capability.

## Prerequisites
- Reel package in `content/ready-to-publish/{{topic_slug}}/`
- `validation-report.md` shows all checks passing
- Instagram MCP authenticated with Facebook Login account (for file upload)
- Publishing quota available (< 100/24hrs)

## Inputs
| Parameter | Description | Required |
|-----------|-------------|----------|
| `package_path` | Path to ready-to-publish package | Yes |
| `account_name` | Connected account name (from `list_accounts`) | No (uses preferred) |
| `schedule_time` | ISO timestamp for scheduled publish | No (immediate if omitted) |
| `confirm_publish` | Whether to actually publish (vs stage only) | Yes |

## Safety Gates
1. **Pre-flight validation** — All specs met, quota available
2. **Human approval** — Explicit confirmation required
3. **Staging first** — Container created, reviewed, then published
4. **Audit log** — Every attempt logged

---

## Step-by-Step Execution

### Step 1: Load Package & Validate

```bash
# Read package manifest
cat content/ready-to-publish/{{topic_slug}}/package-manifest.json

# Verify validation report
cat content/ready-to-publish/{{topic_slug}}/validation-report.md

# Check file exists and specs
ls -la content/ready-to-publish/{{topic_slug}}/final-reel.mp4
```

**Verify:**
- [ ] Manifest status = "ready-for-review"
- [ ] Validation report: ALL PASS
- [ ] File size < 300MB
- [ ] Duration 3-90s
- [ ] Resolution 1080x1920
- [ ] Caption & hashtags loaded

---

### Step 2: Check Publishing Quota

```bash
instagram-mcp call get_publishing_limit --args '{"account": "{{account_name}}"}'
```

**Verify:**
- [ ] Posts remaining > 0
- [ ] Not near 24hr reset boundary

---

### Step 3: Verify Authentication

```bash
instagram-mcp call list_accounts
instagram-mcp call whoami --args '{"account": "{{account_name}}"}'
instagram-mcp call token_status
```

**Verify:**
- [ ] Account shows `facebook_login` tier (required for file upload)
- [ ] Token not expiring soon
- [ ] Correct Instagram account linked

---

### Step 4: Stage Container (Draft)

```bash
# Read caption from package
CAPTION=$(cat content/ready-to-publish/{{topic_slug}}/caption.md)

# Create container - NOTHING GOES PUBLIC YET
instagram-mcp call create_container \
  --args '{
    "account": "{{account_name}}",
    "file": "content/ready-to-publish/{{topic_slug}}/final-reel.mp4",
    "caption": "'$CAPTION'",
    "media_type": "REELS"
  }'
```

**Save container ID:** `{{container_id}}`

**Expected:** Returns container ID with status `IN_PROGRESS`

---

### Step 5: Monitor Container Processing

```bash
# Poll until FINISHED or ERROR (max 24 hours)
instagram-mcp call get_container_status --args '{"container_id": "{{container_id}}"}'
```

**Statuses:**
- `IN_PROGRESS` → Wait 30s, check again
- `FINISHED` → Ready to publish
- `ERROR` → Check error, retry or debug
- `EXPIRED` → Container expired (24hr), recreate

**Wait for:** `FINISHED` status

---

### Step 6: Human Approval Gate

**⚠️ MANDATORY PAUSE — Requires explicit human confirmation**

```
Package: {{topic_slug}}
Container: {{container_id}}
Account: @{{account_handle}}
Caption: {{caption_preview}}
Hashtags: {{hashtag_count}} tags
Video: {{duration}}s, {{size}}MB

CONFIRM PUBLISH? (yes/no)
```

**Only proceed with explicit "yes"**

---

### Step 7: Publish Container

```bash
# WITH confirm: true - THIS GOES LIVE
instagram-mcp call publish_container \
  --args '{"container_id": "{{container_id}}", "account": "{{account_name}}"}' \
  --confirm
```

**Expected:** Returns media ID and permalink

**Save:** `media_id`, `permalink`, `published_timestamp`

---

### Step 8: Verify Publication

```bash
# Check media appears in account
instagram-mcp call get_media_by_id --args '{"media_id": "{{media_id}}", "account": "{{account_name}}"}'

# Verify permalink works
# Open permalink in browser
```

**Verify:**
- [ ] Post visible on profile
- [ ] Caption correct
- [ ] Hashtags rendered
- [ ] Video plays correctly
- [ ] No processing errors

---

### Step 9: Archive & Log

```bash
# Move to published archive
mv content/ready-to-publish/{{topic_slug}} content/published/{{topic_slug}}-{{timestamp}}/

# Update manifest
jq '.status = "published" | .published_at = "'$(date -Iseconds)'" | .media_id = "{{media_id}}" | .permalink = "{{permalink}}"' \
  content/published/{{topic_slug}}-{{timestamp}}/package-manifest.json \
  > content/published/{{topic_slug}}-{{timestamp}}/package-manifest.json.tmp && \
mv content/published/{{topic_slug}}-{{timestamp}}/package-manifest.json.tmp \
  content/published/{{topic_slug}}-{{timestamp}}/package-manifest.json

# Log to automation log
echo "$(date -Iseconds),publish,{{topic_slug}},{{media_id}},{{permalink}},success" >> automation/logs/publishing-log.csv
```

---

### Step 10: Post-Publish Actions (Optional)

```bash
# Add to story highlight (if applicable)
# Pin to profile (if flagship content)
# Share to connected Facebook Page
# Notify team/community
```

---

## Scheduled Publishing (Alternative)

If `schedule_time` provided:

```bash
# Stage container now
# Calculate delay until schedule_time
# Use local scheduler (cron/Task Scheduler) to run publish_container at target time
# Container expires in 24 hours - schedule must be within that window
```

**Windows Task Scheduler Example:**
```powershell
$action = New-ScheduledTaskAction -Execute 'instagram-mcp' -Argument 'call publish_container --args '"'"'{"container_id": "'{{container_id}}'", "account": "'{{account_name}}"'"'"'} --confirm'
$trigger = New-ScheduledTaskTrigger -Once -At {{schedule_time}}
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "IG-Publish-{{topic_slug}}"
```

---

## Rollback / Error Recovery

| Scenario | Action |
|----------|--------|
| Container ERROR | Check error, fix video/caption, recreate container |
| Container EXPIRED | Recreate container from same file |
| Publish fails (quota) | Wait for quota reset, retry |
| Publish fails (auth) | Refresh token, retry |
| Wrong content published | Delete via Instagram app immediately, investigate |
| Caption error post-publish | Edit caption in Instagram app (no MCP edit tool) |

---

## Verification Checklist

Post-publish verification:
- [ ] Post live at permalink
- [ ] Video plays full duration
- [ ] Caption matches approved version
- [ ] All hashtags clickable
- [ ] Audio works
- [ ] No copyright flags
- [ ] Logged in publishing-log.csv
- [ ] Archived to published/

---

## MCP Commands Quick Reference

```bash
# Pre-checks
instagram-mcp call list_accounts
instagram-mcp call get_publishing_limit --args '{"account": "NAME"}'
instagram-mcp call token_status

# Stage
instagram-mcp call create_container --args '{"account": "NAME", "file": "PATH", "caption": "CAP", "media_type": "REELS"}'

# Monitor
instagram-mcp call get_container_status --args '{"container_id": "ID"}'

# Publish (CONFIRM REQUIRED)
instagram-mcp call publish_container --args '{"container_id": "ID", "account": "NAME"}' --confirm

# Verify
instagram-mcp call get_media_by_id --args '{"media_id": "ID", "account": "NAME"}'
```

---

## Important Notes

- **Facebook Login required** for file upload (Instagram Login doesn't support resumable upload)
- **Container expires in 24 hours** — publish within window
- **No native scheduling** — use local scheduler for timed posts
- **100 posts/24hrs limit** — includes all API clients
- **Carousel counts as 1 post** but 50/day limit per carousel section
- **Always stage first** — `create_container` is free, reversible, reviewable
- **Never publish without explicit human confirmation** — this workflow enforces it