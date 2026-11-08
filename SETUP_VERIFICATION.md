# Final Setup Verification Checklist

## ✅ Completed (Automated)

| Component | Status | Details |
|-----------|--------|---------|
| **Environment Inspection** | ✅ Done | Python 3.13.3, Git 2.51, Node 24.20, npm 12.2, uv 0.12.7, FFmpeg 8.1, Claude Code 2.1.302 |
| **Instagram MCP Installation** | ✅ Done | Cloned from https://github.com/thenavidm/instagram-mcp, installed via `uv tool install`, version 0.5.0 |
| **MCP Registration** | ✅ Done | Registered with Claude Code user scope (`claude mcp add --scope user instagram`) |
| **Workspace Structure** | ✅ Done | Complete directory tree created at `~/Instagram-AI-Automation/` |
| **Templates** | ✅ Done | 7 templates: reel-script, reel-hooks, caption, hashtag-strategy, content-calendar, performance-report, competitor-analysis, comment-reply-drafts |
| **Workflows** | ✅ Done | 6 workflows: create-reel-package, publish-reel, daily-snapshot, weekly-report, hashtag-research, comment-triage |
| **Scripts** | ✅ Done | PowerShell & Batch scripts for daily automation |
| **Configuration** | ✅ Done | Complete settings.yaml with all configuration options |
| **Documentation** | ✅ Done | README.md, Meta App Setup Guide |

---

## ⏳ Requires Your Action (Meta Developer Setup)

### Step 1: Create Meta Developer App
**Follow:** `config/meta-app-setup-guide.md`

1. Go to: https://developers.facebook.com/apps/creation/
2. App Name: `Instagram AI Automation`
3. Use Case: **"Manage messaging and content on Instagram"** ← CRITICAL
4. Business: "I don't want to connect a business portfolio yet" (OK for start)
5. Complete creation

### Step 2: Add Permissions
In **Permissions and Features**, add all 8:
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_comments`
- `instagram_manage_insights`
- `instagram_manage_messages`
- `pages_show_list`
- `pages_read_engagement`
- `business_management`

### Step 3: Generate Short-Lived Token
1. Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Add all 8 permissions
4. Generate Access Token
5. Copy token (expires in ~1 hour)

### Step 4: Exchange for Long-Lived Token
```bash
instagram-mcp token \
  --app-id YOUR_APP_ID \
  --app-secret YOUR_APP_SECRET \
  --short-token YOUR_SHORT_TOKEN \
  --path facebook
```

### Step 5: Configure MCP Credentials

**Option A: Accounts File (Recommended)**
1. Save token output JSON to: `config/accounts.json`
2. Update MCP:
```bash
claude mcp remove instagram -s user
claude mcp add --transport stdio instagram \
  --env IG_ACCOUNTS_FILE=C:/Users/saipa/Instagram-AI-Automation/config/accounts.json \
  --scope user \
  -- instagram-mcp
```

**Option B: Environment Variables**
```bash
claude mcp remove instagram -s user
claude mcp add --transport stdio instagram \
  --env IG_ACCESS_TOKEN=YOUR_LONG_LIVED_TOKEN \
  --env IG_USER_ID=YOUR_IG_USER_ID \
  --env IG_HOST=graph.facebook.com \
  --scope user \
  -- instagram-mcp
```

---

## ✅ Post-Setup Verification

Run these commands to verify everything works:

```bash
# 1. Check MCP connection
claude mcp get instagram

# 2. Run doctor (should show your account)
instagram-mcp doctor

# 3. List accounts
instagram-mcp call list_accounts

# 4. Test profile read
instagram-mcp call whoami --args '{"account": "main"}'

# 5. Test media read
instagram-mcp call get_media --args '{"account": "main", "limit": 3}'

# 6. Test publishing quota
instagram-mcp call get_publishing_limit --args '{"account": "main"}'

# 7. Test hashtag search (Facebook Login only)
instagram-mcp call search_hashtag --args '{"hashtag": "test"}'

# 8. Test competitor discovery (Facebook Login only)
instagram-mcp call discover_account --args '{"username": "instagram"}'

# 9. Test comment read
instagram-mcp call read_all_comments --args '{"account": "main", "limit": 10}'

# 10. Test analytics
instagram-mcp call get_account_insights --args '{"account": "main", "period": "day"}'
```

### Expected Doctor Output (Success)
```
instagram-mcp 0.5.0
Graph version: v26.0 (newest known: v26.0)
Data directory: C:\Users\saipa\AppData\Local\instagram-mcp

Token main (facebook_login): OK, @yourhandle (business), 10000 followers, 500 posts
  Account insights: followers_count, impressions, reach, profile_views, ...
  business_discovery: OK (probe returned 500000000 followers)

Unofficial tier: no session
```

---

## 🎯 Feature Status After Setup

| Feature | Status | Notes |
|---------|--------|-------|
| **Read Profile/Media** | ✅ Working | Requires `instagram_basic` |
| **Publish Reels** | ✅ Working | Requires `instagram_content_publish` + Facebook Login |
| **Publish Images** | ⚠️ URL Only | Images need public URL (Meta limitation) |
| **Publish Carousels** | ✅ Working | Mix of URLs and video files |
| **Publish Stories** | ✅ Working | Video files supported |
| **Read Comments** | ✅ Working | Requires `instagram_manage_comments` |
| **Reply to Comments** | ✅ Working | Requires confirmation |
| **Hide/Delete Comments** | ✅ Working | Hide reversible, delete permanent |
| **Read DMs** | ⚠️ Needs App Review | Requires Advanced Access for `instagram_manage_messages` |
| **Send DMs** | ⚠️ Needs App Review | Same as above |
| **Account Insights** | ✅ Working | Requires `instagram_manage_insights` |
| **Media Insights** | ✅ Working | Reach, impressions, engagement |
| **Growth History** | ✅ Working | Local store, builds over time |
| **Post Movement** | ✅ Working | Tracks posts still gaining traction |
| **Hashtag Search** | ✅ Working | Facebook Login only |
| **Hashtag Top/Recent Media** | ✅ Working | Facebook Login only |
| **Competitor Discovery** | ✅ Working | Facebook Login only (`discover_account`) |
| **Account Comparison** | ✅ Working | Facebook Login only (`compare_accounts`) |
| **Audio Search** | ✅ Working | Facebook Login only (Instagram music library) |
| **Container Staging** | ✅ Working | 24hr draft state |
| **Scheduling** | ✅ Local Only | Windows Task Scheduler + container workflow |
| **Token Refresh** | ✅ Auto | `instagram-mcp refresh` for Instagram Login tokens |

---

## 🔒 Security Checklist

- [ ] Tokens stored in `config/accounts.json` (gitignored)
- [ ] No tokens in Git history
- [ ] No tokens in terminal output/logs
- [ ] Windows Credential Manager used for sensitive values
- [ ] `IG_READ_ONLY=1` set for read-only testing if needed
- [ ] Unofficial tier disabled (`IG_UNOFFICIAL=0` or unset)
- [ ] Audit logging enabled (`IG_AUDIT_LOG`)

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `config/settings.yaml` | All configuration |
| `config/meta-app-setup-guide.md` | Meta App setup instructions |
| `config/accounts.json` | **Your credentials (gitignored)** |
| `config/templates/*.md` | Content templates |
| `automation/workflows/*.md` | Automation workflows |
| `automation/scripts/*.ps1` | Scheduled task scripts |
| `instagram-mcp/` | Cloned MCP repository |

---

## 🚀 Next Steps After Verification

1. **Test Read Operations** - Verify all read tools work
2. **Create First Reel Package** - Run `create-reel-package` workflow
3. **Stage & Review** - Use `publish-reel` workflow (stages first)
4. **Approve & Publish** - Human confirmation required
5. **Set Up Automation** - Configure Windows Task Scheduler for daily/weekly tasks
6. **Build Content Calendar** - Use templates to plan 7-30 days
7. **Run Competitor Analysis** - Identify gaps and opportunities
8. **Establish Comment Routine** - Daily triage at 9 AM / 3 PM

---

## 📞 Support

- **Instagram MCP Issues:** https://github.com/thenavidm/instagram-mcp/issues
- **Meta Graph API Docs:** https://developers.facebook.com/docs/instagram-platform/
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/

---

*Generated by Instagram AI Automation Setup • All automated components complete • Meta App setup requires your action*