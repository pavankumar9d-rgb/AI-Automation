# Comment Triage & Reply Workflow

## Overview
Daily workflow to read, categorize, draft replies, and respond to Instagram comments.

## Prerequisites
- Instagram MCP authenticated
- Comment reply templates loaded (`config/templates/comment-reply-drafts.md`)

## Schedule
Run daily (recommended: 9 AM and 3 PM)

## Inputs
| Parameter | Description | Required |
|-----------|-------------|----------|
| `account_name` | Target account | Yes |
| `lookback_days` | How far back to check | No (default: 1) |
| `auto_reply` | Actually post replies (vs draft only) | No (default: false) |

## Outputs
- `automation/logs/comment-triage-{{date}}.json` — Full triage log
- `automation/logs/comment-replies-{{date}}.json` — Replies posted
- `content/captions/pending-replies-{{date}}.md` — Drafts pending approval

---

## Step-by-Step Execution

### Step 1: Fetch All Recent Comments

```bash
# Get comments across all recent posts (efficient batch)
instagram-mcp call read_all_comments --args '{"account": "{{account_name}}", "limit": 100}'
```

**Alternative (per-post):**
```bash
# Get recent media
instagram-mcp call get_media --args '{"account": "{{account_name}}", "limit": 10}'

# For each media, get comments
instagram-mcp call get_comments --args '{"media_id": "{{media_id}}", "account": "{{account_name}}"}'
```

---

### Step 2: Categorize Each Comment

**Categories:**
| Category | Keywords/Patterns | Priority | Action |
|----------|-------------------|----------|--------|
| Question | ?, how, what, why, where, which, can you | HIGH | Reply with answer |
| Compliment | love, amazing, great, awesome, thank, inspiring | MEDIUM | Appreciation reply |
| Feedback | suggest, improve, missing, wrong, correction | MEDIUM | Acknowledge |
| Tag/Mention | @username | MEDIUM | Engage |
| Complaint | broken, doesn't work, disappointed, issue | HIGH | Support reply |
| Sales/Intent | price, buy, link, where to get, sign up | HIGH | Sales reply |
| UGC/Feature | feature me, I made this, check mine | MEDIUM | UGC reply |
| Spam/Bot | irrelevant, promo, follow me, crypto, onlyfans | NONE | Hide/Delete |
| Negative/Troll | hate, worst, stupid, attack, insult | LOW | Boundary/Hide |
| Emoji Only | 🔥💯❤️👏😂🙌 | LOW | Emoji reply |

---

### Step 3: Filter & Prioritize

**Priority Order:**
1. **Sales/Buying Intent** — Revenue impact
2. **Questions** — Educational value, SEO
3. **Complaints/Issues** — Reputation management
4. **Compliments** — Community building
5. **Tags/Mentions** — Engagement
6. **Feedback** — Product improvement
7. **UGC Requests** — Content pipeline
8. **Emoji Reactions** — Light engagement
9. **Negative/Trolls** — Boundary setting
10. **Spam** — Hide/Delete

---

### Step 4: Draft Replies

For each comment needing reply:
1. Select appropriate template from `comment-reply-drafts.md`
2. Personalize with:
   - Commenter's name (if available)
   - Specific reference to their comment
   - Relevant value-add
3. Keep under 2,200 characters
4. Add 0-3 relevant emojis
5. Include CTA only if natural

**Save drafts to:** `content/captions/pending-replies-{{date}}.md`

Format:
```markdown
## Comment: {{comment_id}}
**Post:** {{media_id}} | **Author:** @{{username}} | **Type:** {{category}}
**Comment:** "{{comment_text}}"

**Draft Reply:**
{{personalized_reply}}

**Action:** [ ] Approve [ ] Edit [ ] Skip
```

---

### Step 5: Human Approval Gate (Default)

**⚠️ DEFAULT: Drafts only — require approval before posting**

Review each draft:
- [ ] Addresses specific comment
- [ ] Brand voice consistent
- [ ] No compliance issues
- [ ] CTA appropriate
- [ ] No typos

---

### Step 6: Post Approved Replies

```bash
# For each approved reply
instagram-mcp call reply_to_comment \
  --args '{"comment_id": "{{comment_id}}", "message": "{{approved_reply}}", "account": "{{account_name}}"}' \
  --confirm
```

**Track results:**
```json
{
  "comment_id": "{{comment_id}}",
  "reply_text": "{{reply}}",
  "posted_at": "{{timestamp}}",
  "success": true,
  "reply_id": "{{reply_id}}"
}
```

---

### Step 7: Handle Special Actions

**Hide Spam/Inappropriate:**
```bash
instagram-mcp call hide_comment --args '{"comment_id": "{{comment_id}}", "account": "{{account_name}}"}'
```

**Delete (Permanent, Rare):**
```bash
instagram-mcp call delete_comment --args '{"comment_id": "{{comment_id}}", "account": "{{account_name}}"}' --confirm
```

**Private Reply (One per comment, for sensitive):**
```bash
instagram-mcp call private_reply_to_comment --args '{"comment_id": "{{comment_id}}", "message": "{{private_msg}}", "account": "{{account_name}}"}' --confirm
```

---

### Step 8: Log & Analyze

**Daily Log Entry:**
```json
{
  "date": "{{date}}",
  "account": "{{account_name}}",
  "total_comments": {{count}},
  "by_category": {
    "question": {{n}},
    "compliment": {{n}},
    "complaint": {{n}},
    "sales": {{n}},
    "spam": {{n}},
    "negative": {{n}}
  },
  "replies_drafted": {{n}},
  "replies_posted": {{n}},
  "comments_hidden": {{n}},
  "comments_deleted": {{n}},
  "avg_response_time_minutes": {{avg}},
  "top_questions": ["{{q1}}", "{{q2}}"],
  "sentiment": {"positive": {{pct}}, "neutral": {{pct}}, "negative": {{pct}}}
}
```

**Weekly Analysis:**
- Most asked questions → FAQ content ideas
- Sentiment trend → Community health
- Response rate → Engagement quality
- Unanswered themes → Content gaps

---

## Automation (Windows Task Scheduler)

```powershell
# Morning run
$trigger1 = New-ScheduledTaskTrigger -Daily -At 09:00
# Afternoon run
$trigger2 = New-ScheduledTaskTrigger -Daily -At 15:00
```

---

## MCP Commands Reference

```bash
# Batch read all comments (recommended)
instagram-mcp call read_all_comments --args '{"account": "NAME", "limit": 100}'

# Per-post comments
instagram-mcp call get_comments --args '{"media_id": "ID", "account": "NAME"}'

# Comment replies
instagram-mcp call get_comment_replies --args '{"comment_id": "ID", "account": "NAME"}'

# Reply (confirm required)
instagram-mcp call reply_to_comment --args '{"comment_id": "ID", "message": "REPLY", "account": "NAME"}' --confirm

# Hide (reversible)
instagram-mcp call hide_comment --args '{"comment_id": "ID", "account": "NAME"}'

# Delete (permanent, confirm required)
instagram-mcp call delete_comment --args '{"comment_id": "ID", "account": "NAME"}' --confirm

# Private reply (confirm required, one per comment)
instagram-mcp call private_reply_to_comment --args '{"comment_id": "ID", "message": "MSG", "account": "NAME"}' --confirm
```

---

## Response Time Targets

| Comment Type | Target Response | Max Response |
|--------------|-----------------|--------------|
| Sales Intent | <30 min | 2 hours |
| Questions | <1 hour | 4 hours |
| Complaints | <1 hour | 2 hours |
| Compliments | <2 hours | 8 hours |
| Tags/Mentions | <2 hours | 8 hours |
| Feedback | <4 hours | 24 hours |
| UGC Requests | <2 hours | 8 hours |
| Emoji Only | <8 hours | 24 hours |
| Negative/Trolls | <4 hours | 8 hours |

---

## Escalation Rules

| Situation | Action |
|-----------|--------|
| Legal threat in comments | Screenshot, hide, legal review immediately |
| Viral negative thread | Don't engage, monitor, prepare statement |
| Competitor attack | Document, don't engage publicly |
| Personal data exposed | Hide immediately, DM user, report to Meta |
| Coordinated spam attack | Bulk hide, adjust filters, report |

---

## Quality Checklist (Per Reply)

- [ ] Uses commenter's name (if visible)
- [ ] References specific part of their comment
- [ ] Adds value (answer, insight, warmth, direction)
- [ ] Brand voice consistent
- [ ] Under 2,200 characters
- [ ] 0-3 emojis (not excessive)
- [ ] CTA only if natural
- [ ] No medical/financial/legal advice
- [ ] No controversial opinions
- [ ] Grammar/spelling checked