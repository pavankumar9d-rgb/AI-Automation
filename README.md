# Instagram AI Automation Workspace

A complete Instagram Creator account automation environment controlled through Claude Code, with content production, publishing, research, analytics, comment management and scheduling capabilities.

## 📁 Workspace Structure

```
Instagram-AI-Automation/
├── content/
│   ├── ideas/           # Content ideas and concepts
│   ├── scripts/         # Reel/video scripts
│   ├── generated-videos/ # AI-generated video files
│   ├── thumbnails/      # Thumbnail images
│   ├── captions/        # Caption drafts
│   ├── ready-to-publish/ # Final content ready for publishing
│   └── published/       # Published content archive
├── analytics/
│   ├── daily/           # Daily analytics snapshots
│   ├── weekly/          # Weekly reports
│   └── monthly/         # Monthly reports
├── research/
│   ├── competitors/     # Competitor analysis
│   ├── hashtags/        # Hashtag research
│   └── trends/          # Trending content research
├── automation/
│   ├── workflows/       # Reusable automation workflows
│   └── logs/            # Execution logs
├── config/              # Configuration files
├── reports/             # Generated reports
└── instagram-mcp/       # Instagram MCP server (cloned repo)
```

## 🚀 Quick Start

### 1. Meta Developer App Setup

1. Go to [developers.facebook.com/apps/creation](https://developers.facebook.com/apps/creation/)
2. Create a new app → Select "Manage messaging and content on Instagram"
3. Add required permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_comments`
   - `instagram_manage_insights`
   - `instagram_manage_messages`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`
4. Generate a short-lived token from the app dashboard

### 2. Get Long-Lived Token

```bash
instagram-mcp token \
  --app-id YOUR_APP_ID \
  --app-secret YOUR_APP_SECRET \
  --short-token YOUR_SHORT_TOKEN \
  --path facebook
```

### 3. Configure MCP in Claude Code

```bash
claude mcp add --transport stdio instagram \
  --env IG_ACCESS_TOKEN=your_long_lived_token \
  --env IG_USER_ID=your_ig_user_id \
  --scope user \
  -- instagram-mcp
```

### 4. Verify Setup

```bash
instagram-mcp doctor
```

## 🎯 Available Workflows

| Command | Description |
|---------|-------------|
| "Analyze my Instagram account" | Full account analysis |
| "Find my best-performing Reel" | Top content identification |
| "Research 10 competitors" | Competitor analysis |
| "Find hashtags for my next Reel" | Hashtag research |
| "Create 5 new Reel concepts" | Content ideation |
| "Generate a complete Reel production package" | End-to-end content creation |
| "Prepare this video for publishing" | Pre-publish validation |
| "Publish the approved Reel" | Safe publishing with confirmation |
| "Analyze my latest comments" | Comment sentiment analysis |
| "Draft replies to unanswered comments" | Engagement management |
| "Prepare my weekly growth report" | Analytics reporting |
| "Build my next 7-day content calendar" | Content planning |

## 📋 Templates

See `config/templates/` for:
- Reel scripts
- Reel hooks
- Captions
- Hashtag sets
- Content calendars
- Performance reports
- Competitor analysis
- Comment reply drafts

## 🔒 Security Notes

- Never commit credentials to Git
- Use Windows Credential Manager or environment variables
- Tokens are never printed in logs
- All write operations require explicit confirmation
- Unofficial tier is disabled by default

## 📚 Documentation

- [Instagram MCP README](instagram-mcp/README.md)
- [Meta Graph API Docs](https://developers.facebook.com/docs/instagram-platform/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## ⚠️ Important Limitations

- Instagram API requires Business or Creator account
- No native scheduling - uses local task scheduler
- 100 posts/24hrs API limit
- 30 unique hashtags/7 days limit
- DMs require 24-hour window or private reply
- Some insights require Meta App Review

---

Built with [Instagram MCP](https://github.com/thenavidm/instagram-mcp) and Claude Code.