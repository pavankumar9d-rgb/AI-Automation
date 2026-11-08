# Automation Workflows

This directory contains reusable automation workflows for the Instagram AI Automation system.

## Workflow Categories

### 1. Content Production Workflows
- `create-reel-package.md` — End-to-end Reel creation from topic to ready-to-publish
- `batch-content-creation.md` — Create multiple content pieces in one session
- `content-calendar-planning.md` — Plan 7/30-day content calendar

### 2. Publishing Workflows
- `publish-reel.md` — Safe Reel publishing with validation
- `publish-carousel.md` — Carousel publishing workflow
- `stage-and-schedule.md` — Container staging for later publishing
- `publishing-queue.md` — Queue management and scheduling

### 3. Analytics Workflows
- `daily-snapshot.md` — Daily metrics collection
- `weekly-report.md` — Weekly performance report generation
- `monthly-report.md` — Monthly deep-dive report
- `competitor-analysis.md` — Competitor benchmarking

### 4. Engagement Workflows
- `comment-triage.md` — Daily comment analysis and reply drafting
- `dm-management.md` — DM reading and response workflow
- `community-health.md` — Weekly community sentiment check

### 5. Research Workflows
- `hashtag-research.md` — Hashtag discovery and validation
- `trend-monitoring.md` — Trending content detection
- `content-gap-analysis.md` — Identify content opportunities

### 6. Maintenance Workflows
- `token-refresh.md` — Token health check and renewal
- `doctor-check.md` — System health verification
- `quota-monitoring.md` — API quota tracking

---

## Workflow Execution

Each workflow is a markdown file with:
1. **Prerequisites** — What must be true before running
2. **Inputs** — Required parameters/data
3. **Steps** — Sequential MCP commands and logic
4. **Outputs** — Files created, data saved
5. **Verification** — How to confirm success
6. **Error Handling** — Common failures and recovery

Run workflows by invoking the steps manually or via Claude Code with the appropriate prompts.