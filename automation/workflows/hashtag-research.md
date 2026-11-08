# Hashtag Research Workflow

## Overview
Discover, validate, and organize hashtags for content strategy using official Instagram Graph API.

## Prerequisites
- Instagram MCP with Facebook Login account (required for hashtag tools)
- `business_discovery` permission working (verified via `doctor`)

## Inputs
| Parameter | Description | Required |
|-----------|-------------|----------|
| `seed_topics` | List of core topics/keywords | Yes |
| `competitor_accounts` | Accounts to mine hashtags from | No |
| `target_count` | Desired hashtag pool size | No (default: 50) |

## Outputs
- `research/hashtags/{{date}}-hashtag-research.md` — Research findings
- `research/hashtags/{{date}}-validated-hashtags.json` — Validated hashtag bank
- `research/hashtags/{{date}}-hashtag-sets.md` — Organized sets by content type

---

## Step-by-Step Execution

### Phase 1: Seed Hashtag Discovery

```bash
# For each seed topic
for TOPIC in "{{seed_topics}}"; do
  # Search hashtag
  instagram-mcp call search_hashtag --args '{"hashtag": "'$TOPIC'"}'
  
  # Get top media (shows what's performing)
  instagram-mcp call hashtag_top_media --args '{"hashtag": "'$TOPIC'"}'
  
  # Get recent media (shows what's being posted now)
  instagram-mcp call hashtag_recent_media --args '{"hashtag": "'$TOPIC'"}'
done
```

**Capture for each:**
- Hashtag ID
- Post count (volume)
- Top post engagement rates
- Recent post frequency
- Related hashtags from top posts

---

### Phase 2: Competitor Hashtag Mining

```bash
# For each competitor
for COMP in "{{competitor_accounts}}"; do
  # Get recent posts
  instagram-mcp call get_media --args '{"account": "'$COMP'", "limit": 20}'
  
  # Extract hashtags from captions
  # (requires parsing media captions)
done
```

**Compile:** Unique hashtags used by competitors + their engagement context

---

### Phase 3: Hashtag Validation

For each candidate hashtag, check:

```bash
instagram-mcp call search_hashtag --args '{"hashtag": "CANDIDATE"}'
instagram-mcp call hashtag_top_media --args '{"hashtag": "CANDIDATE"}'
```

**Validation Criteria:**
| Check | Pass Criteria |
|-------|---------------|
| Not banned | "Recent" tab exists, returns results |
| Relevant | Top posts match your niche |
| Volume | 10K - 1M posts (sweet spot) |
| Engagement | Top posts have >2% engagement rate |
| Recency | Recent posts within last hour |
| No spam | Recent posts aren't all bot/spam |

**Mark each:** ✅ Approved | ⚠️ Caution | ❌ Rejected | 🔴 Banned

---

### Phase 4: Organize into Tiered Sets

**Tier 1: Niche-Specific (High relevance, 10K-100K posts)**
```
#{{specific_tag_1}} #{{specific_tag_2}} ...
```

**Tier 2: Category/Industry (Medium relevance, 100K-1M posts)**
```
#{{category_tag_1}} #{{category_tag_2}} ...
```

**Tier 3: Broad Discovery (Low relevance, 1M+ posts)**
```
#{{broad_tag_1}} #{{broad_tag_2}} ...
```

**Tier 4: Branded/Community (Unique to you)**
```
#{{your_brand}} #{{your_series}} ...
```

**Tier 5: Trending/Seasonal (Time-sensitive)**
```
#{{trending_now}} #{{seasonal}} ...
```

---

### Phase 5: Create Rotation Schedule

**Weekly Rotation Plan (avoids 30 unique/7-day limit):**

| Day | Primary Tier | Secondary Tier | Test Slots (2-3 new) |
|-----|--------------|----------------|---------------------|
| Mon | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_1}} #{{new_2}} |
| Tue | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_3}} #{{new_4}} |
| Wed | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_5}} #{{new_6}} |
| Thu | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_7}} #{{new_8}} |
| Fri | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_9}} #{{new_10}} |
| Sat | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_11}} #{{new_12}} |
| Sun | Tier 1 (5) + Tier 2 (5) | Tier 3 (3) + Tier 4 (2) | #{{new_13}} #{{new_14}} |

**Rule:** Minimum 5 new hashtags per post, never repeat exact 30-tag set 2 days in a row.

---

### Phase 6: Performance Tracking Setup

Create tracking template:

| Hashtag | Tier | Posts Used | Total Reach | Avg Reach/Post | Avg Eng Rate | Status |
|---------|------|------------|-------------|----------------|--------------|--------|
| #{{tag}} | 1 | 0 | 0 | 0 | 0% | Testing |

---

## Output Files

### `{{date}}-validated-hashtags.json`
```json
{
  "research_date": "{{date}}",
  "seed_topics": [...],
  "competitors_analyzed": [...],
  "hashtags": [
    {
      "tag": "{{tag}}",
      "id": "{{hashtag_id}}",
      "post_count": {{count}},
      "tier": 1,
      "validation": "approved",
      "top_post_engagement": {{rate}},
      "recent_frequency_per_hour": {{freq}},
      "related_tags": [...],
      "source": "seed|competitor|related",
      "status": "testing|active|retired|banned"
    }
  ]
}
```

### `{{date}}-hashtag-sets.md`
Markdown with ready-to-copy sets for each content type.

---

## MCP Commands Reference

```bash
# Search hashtag (get ID and basic info)
instagram-mcp call search_hashtag --args '{"hashtag": "TAG"}'

# Top performing content for hashtag
instagram-mcp call hashtag_top_media --args '{"hashtag": "TAG"}'

# Recent content for hashtag
instagram-mcp call hashtag_recent_media --args '{"hashtag": "TAG"}'

# Discover competitor account (get their posts)
instagram-mcp call discover_account --args '{"username": "COMPETITOR"}'

# Compare accounts (see their engagement)
instagram-mcp call compare_accounts --args '{"accounts": ["A", "B", "C"]}'
```

---

## Important Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Unique hashtags/7 days | 30 | Resolved IDs cached locally |
| Hashtags per post | 30 | Instagram hard limit |
| `search_hashtag` calls | Rate limited | Cache results |
| `business_discovery` | FB Login only | Not available on Instagram Login |

---

## Banned Hashtag Detection

**Signs a hashtag is banned/shadowbanned:**
1. Search returns hashtag but "Recent" tab missing
2. "Recent" tab shows "No results found"
3. Top posts are all from years ago
4. Sudden drop to zero reach when using it

**Action:** Mark 🔴 Banned in database, remove from all sets, test alternatives.

---

## Monthly Maintenance

1. Re-validate all active hashtags
2. Retire consistently low-performing tags
3. Add 10-20 new test hashtags
4. Update rotation schedule
5. Archive old research files