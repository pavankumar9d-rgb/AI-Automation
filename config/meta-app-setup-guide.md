# Meta Developer App Setup Guide

## Overview
Step-by-step guide to create and configure a Meta Developer App for Instagram API access using the **Facebook Login** path (recommended for full capabilities).

---

## Prerequisites
- Facebook account (personal)
- Instagram **Creator** or **Business** account (NOT personal)
- Instagram account linked to a Facebook Page
- Admin access to that Facebook Page

---

## Step 1: Create Meta App

### 1.1 Navigate to App Creation
1. Go to: https://developers.facebook.com/apps/creation/
2. Log in with your Facebook account

### 1.2 App Details
- **App Name:** `Instagram AI Automation` (or your preferred name)
- **App Contact Email:** Your email
- **Business Account:** Select your business portfolio or "I don't want to connect a business portfolio yet"
- Click **Next**

### 1.3 Use Case Selection
**CRITICAL:** Select **"Manage messaging and content on Instagram"**

> ⚠️ **Do NOT select:**
> - "Other" → This is the old flow
> - "Business" as app type → No longer exists
> - "Instagram API" as product → Doesn't exist as separate option

The use case "Manage messaging and content on Instagram" automatically adds the Instagram Graph API product.

### 1.4 Complete Creation
- Click **Next** → Review → **Go to Dashboard**

---

## Step 2: Configure Instagram Product

### 2.1 Access Instagram Settings
1. In left sidebar: **Products** → **Instagram** → **Settings**
2. Or: **API Setup with Instagram Login** (left menu)

### 2.2 Add Permissions (Facebook Login Path)
Go to **Permissions and Features** in left menu.

**Add these permissions (Required for full functionality):**

| Permission | Purpose | Required For |
|------------|---------|--------------|
| `instagram_basic` | Read profile, media | All read operations |
| `instagram_content_publish` | Publish reels, posts, stories | Publishing |
| `instagram_manage_comments` | Read/reply/hide comments | Comment management |
| `instagram_manage_insights` | Reach, impressions, engagement | Analytics |
| `instagram_manage_messages` | Read/send DMs | DM management |
| `pages_show_list` | Find connected Pages | Account discovery |
| `pages_read_engagement` | Read Page insights | Page analytics |
| `business_management` | Required by Meta for messaging | All messaging features |

**For each permission:**
1. Click **Add** next to permission
2. Follow any additional setup prompts

> 💡 **Tip:** Use "Add all required permissions" button if available for the "Manage messaging and content on Instagram" use case.

---

## Step 3: Generate Access Token

### 3.1 Short-Lived Token (User Token)
1. Go to **API Setup with Facebook Login** (left menu)
2. Or: **Graph API Explorer** → https://developers.facebook.com/tools/explorer/
3. Select your app from dropdown
4. Add all permissions listed above
5. Click **Generate Access Token**
6. Approve the login dialog
7. **Copy the token** — this is your **short-lived user token** (~1 hour)

> ⚠️ **Important:** This token expires in ~1 hour. You must exchange it for a long-lived token immediately.

---

## Step 4: Exchange for Long-Lived Token

### 4.1 Using Instagram MCP (Recommended)
```bash
instagram-mcp token \
  --app-id YOUR_APP_ID \
  --app-secret YOUR_APP_SECRET \
  --short-token YOUR_SHORT_LIVED_TOKEN \
  --path facebook
```

### 4.2 What This Does
- Exchanges short token → long-lived token (60 days for user, **never expires for Page tokens**)
- Finds all Pages you manage with linked Instagram accounts
- Outputs ready-to-use `IG_ACCOUNTS_FILE` JSON

### 4.3 Expected Output
```json
[
  {
    "account_name": "your_ig_username",
    "user_id": "17841400000000000",
    "access_token": "EAAG...",  // Page token - NEVER EXPIRES
    "host": "graph.facebook.com"
  }
]
```

**Save this JSON** — it's your complete configuration.

---

## Step 5: Configure Instagram MCP

### 5.1 Option A: Single Account (Environment Variables)
```bash
claude mcp add --transport stdio instagram \
  --env IG_ACCESS_TOKEN=EAAG... \
  --env IG_USER_ID=17841400000000000 \
  --env IG_HOST=graph.facebook.com \
  --scope user \
  -- instagram-mcp
```

### 5.2 Option B: Multiple Accounts (Accounts File)
1. Save the JSON from Step 4.3 to: `config/accounts.json`
2. Configure MCP:
```bash
claude mcp add --transport stdio instagram \
  --env IG_ACCOUNTS_FILE=C:/Users/saipa/Instagram-AI-Automation/config/accounts.json \
  --scope user \
  -- instagram-mcp
```

### 5.3 Option C: Claude Desktop Config
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "instagram": {
      "command": "C:\\Users\\saipa\\.local\\bin\\instagram-mcp.exe",
      "env": {
        "IG_ACCOUNTS_FILE": "C:\\Users\\saipa\\Instagram-AI-Automation\\config\\accounts.json"
      }
    }
  }
}
```
**Restart Claude Desktop completely after editing.**

---

## Step 6: Verify Installation

```bash
# Check MCP connection
claude mcp get instagram

# Run doctor - THE MOST IMPORTANT COMMAND
instagram-mcp doctor
```

### Expected Doctor Output
```
instagram-mcp 0.5.0
Graph version: v22.0 (newest known: v22.0)
Data directory: C:\Users\saipa\.local\share\instagram-mcp

Token main (facebook_login): OK, @yourhandle (business), 10000 followers, 500 posts
  Account insights: followers_count, impressions, reach, profile_views, ...
  business_discovery: OK (probe returned 500000000 followers)

Unofficial tier: no session
```

### ❌ Common Doctor Failures

| Error | Fix |
|-------|-----|
| "Personal account" | Switch to Creator/Business in Instagram app → Settings → Account Type |
| "Tried accessing nonexisting field" | Regenerate token AFTER adding permissions |
| "business_discovery: FAIL" | Must use Facebook Login path (--path facebook), not Instagram Login |
| "No accounts configured" | Set IG_ACCESS_TOKEN + IG_USER_ID or IG_ACCOUNTS_FILE |

---

## Step 7: Test Core Functions

```bash
# List connected accounts
instagram-mcp call list_accounts

# Get your profile
instagram-mcp call whoami --args '{"account": "main"}'

# Get recent posts
instagram-mcp call get_media --args '{"account": "main", "limit": 5}'

# Check publishing quota
instagram-mcp call get_publishing_limit --args '{"account": "main"}'

# Test hashtag search (Facebook Login only)
instagram-mcp call search_hashtag --args '{"hashtag": "test"}'

# Test competitor discovery (Facebook Login only)
instagram-mcp call discover_account --args '{"username": "instagram"}'
```

---

## Token Management

### Refresh Instagram Login Tokens (Every 60 Days)
```bash
instagram-mcp refresh
```
Updates tokens in place. Copy new tokens to your config.

### Facebook Login Page Tokens
**Never expire.** No refresh needed.

### Token Security
- **NEVER** commit tokens to Git
- **NEVER** share tokens in chat/logs
- Use Windows Credential Manager or environment variables
- Rotate if compromised

---

## App Review (Only If Needed)

**You DO NOT need App Review for:**
- Your own accounts
- Accounts where you're added as Developer/Tester/Admin in App Roles

**You NEED App Review for:**
- Other people logging into your app
- `instagram_manage_messages` Advanced Access (for reading DMs)
- Going live to public users

### To Request Advanced Access for DMs:
1. App Dashboard → **App Review** → **Permissions and Features**
2. Find `instagram_manage_messages` → **Request Advanced Access**
3. Provide screencast/video showing how you use DMs
4. Wait for Meta review (days to weeks)

**Without Advanced Access:** `list_conversations` returns empty, not an error.

---

## Troubleshooting Checklist

- [ ] Instagram account is **Creator** or **Business** (not Personal)
- [ ] Instagram account **linked to Facebook Page**
- [ ] Meta App uses **"Manage messaging and content on Instagram"** use case
- [ ] All 8 permissions added in **Permissions and Features**
- [ ] Token generated **AFTER** permissions added
- [ ] Used `--path facebook` for token exchange
- [ ] `instagram-mcp doctor` shows all green
- [ ] `business_discovery` shows OK in doctor
- [ ] MCP server starts in Claude Code (`/mcp` shows connected)

---

## Quick Reference: App IDs & Secrets

| Location | Value |
|----------|-------|
| App Dashboard → Settings → Basic | App ID, App Secret |
| Graph API Explorer | Generate short-lived tokens |
| App Dashboard → Roles | Add testers/developers |
| App Dashboard → App Review | Request Advanced Access |

---

## Security Best Practices

1. **Separate app per project** — Don't reuse apps across unrelated projects
2. **Minimal permissions** — Only add what you use
3. **Role management** — Add team members as Testers/Developers, not Admins
4. **Token rotation** — Refresh Instagram Login tokens before expiry
5. **Audit log** — Check `IG_AUDIT_LOG` for all write operations
6. **HTTPS only** — Never use HTTP for redirect URLs (not needed for MCP)

---

## Support Resources

- **Instagram MCP Issues:** https://github.com/thenavidm/instagram-mcp/issues
- **Meta Graph API Docs:** https://developers.facebook.com/docs/instagram-platform/
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/
- **App Review Guide:** https://developers.facebook.com/docs/app-review/