# Create Reel Package Workflow

## Overview
End-to-end workflow to create a complete Reel production package from a topic idea to ready-to-publish assets.

## Prerequisites
- Instagram MCP configured and authenticated
- Topic/idea provided
- FFmpeg installed for video processing
- Access to image/video generation tools (if configured)

## Inputs
| Parameter | Description | Required |
|-----------|-------------|----------|
| `topic` | The Reel topic/theme | Yes |
| `target_audience` | Who this is for | Yes |
| `goal` | educate/entertain/inspire/sell | Yes |
| `format` | talking-head/demo/storytelling/POV/before-after | No (default: storytelling) |
| `duration_target` | Target seconds (15-90) | No (default: 30) |
| `brand_voice` | Tone guidelines | No |
| `existing_assets` | Path to any existing footage | No |

## Outputs
Saved to `content/ready-to-publish/{{topic_slug}}/`
- `script.md` — Complete reel script with hooks, beats, CTA
- `shot-list.md` — Detailed shot list with timings
- `caption.md` — Final caption with hashtags
- `voiceover-script.md` — Voiceover narration script
- `editing-plan.md` — FFmpeg editing commands
- `thumbnail-options/` — Thumbnail concepts
- `validation-report.md` — Pre-publish checks

---

## Step-by-Step Execution

### Phase 1: Research & Ideation (5-10 min)

```bash
# 1. Research topic via web search (if web access available)
# 2. Check competitor content on this topic
instagram-mcp call discover_account --args '{"username": "competitor1"}'
instagram-mcp call discover_account --args '{"username": "competitor2"}'
instagram-mcp call compare_accounts --args '{"accounts": ["competitor1", "competitor2"]}'

# 3. Find relevant hashtags
instagram-mcp call search_hashtag --args '{"hashtag": "main_topic_tag"}'
instagram-mcp call hashtag_top_media --args '{"hashtag": "main_topic_tag"}'
instagram-mcp call hashtag_recent_media --args '{"hashtag": "main_topic_tag"}'

# 4. Analyze top-performing content patterns
# Save findings to content/ideas/{{topic_slug}}-research.md
```

**Deliverable:** Research brief with:
- Top 3 competitor approaches
- 10+ validated hashtags
- Content gap opportunities
- Proven hook angles in niche

---

### Phase 2: Concept Development (10-15 min)

**Generate 3 distinct Reel concepts:**

| Concept | Hook Type | Structure | Differentiator |
|---------|-----------|-----------|----------------|
| A | {{hook_a}} | {{struct_a}} | {{diff_a}} |
| B | {{hook_b}} | {{struct_b}} | {{diff_b}} |
| C | {{hook_c}} | {{struct_c}} | {{diff_c}} |

**Select best concept based on:**
- Alignment with goal
- Feasibility with available assets
- Hook strength (retention potential)
- Uniqueness vs competitors

**Save selected concept to:** `content/ideas/{{topic_slug}}-concept.md`

---

### Phase 3: Script Writing (15-20 min)

**Using template:** `config/templates/reel-script.md`

**Write complete script including:**
1. **Hook (0-3s)** — Visual + audio + text
2. **Opening (3-5s)** — Establish context
3. **Value Beats (3-4 beats)** — Each with visual, audio, text, duration
4. **CTA (last 3-5s)** — Clear, single action
5. **Production notes** — Location, lighting, audio, props, B-roll
6. **Post-production** — Music, transitions, color, captions

**Timing check:** Read aloud at natural pace → adjust to hit `duration_target ± 3s`

**Save to:** `content/scripts/{{topic_slug}}-script.md`

---

### Phase 4: Caption & Hashtag Generation (5 min)

**Using template:** `config/templates/caption.md` + `config/templates/hashtag-strategy.md`

**Generate:**
1. Caption (hook → value → CTA → hashtags)
2. Hashtag set (15-30 tags, tiered strategy)
3. Alt text for accessibility

**Save to:** `content/captions/{{topic_slug}}-caption.md`

---

### Phase 5: Voiceover Script (5 min)

**Extract narration from script:**
- Remove visual-only cues
- Add pronunciation guides
- Mark pacing/emphasis
- Include alternatives for A/B testing

**Save to:** `content/scripts/{{topic_slug}}-voiceover.md`

---

### Phase 6: Shot List & Editing Plan (10 min)

**Create detailed shot list:**

| Shot # | Visual Description | Duration | Audio Cue | Text Overlay | Camera/Setup |
|--------|-------------------|----------|-----------|--------------|--------------|
| 1 | | | | | |
| 2 | | | | | |

**Generate FFmpeg editing commands:**

```bash
# Example editing plan saved to editing-plan.md
# 1. Concatenate clips
ffmpeg -f concat -safe 0 -i clip_list.txt -c copy rough_cut.mp4

# 2. Add captions (using filter_complex)
ffmpeg -i rough_cut.mp4 -vf "subtitles=captions.srt" captioned.mp4

# 3. Add music (duck under voiceover)
ffmpeg -i captioned.mp4 -i music.mp3 -filter_complex "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first" final.mp4

# 4. Validate specs
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 final.mp4
# Must be 1080x1920, 30fps, <300MB, 3-90s
```

**Save to:** `content/scripts/{{topic_slug}}-shotlist.md` and `content/scripts/{{topic_slug}}-editing-plan.md`

---

### Phase 7: Asset Production (Variable)

**If using AI generation tools:**
```bash
# Image generation (if configured)
# Video generation (if configured)
# Voiceover TTS (if configured)
```

**If shooting manually:**
- Follow shot list
- Record multiple takes per shot
- Capture B-roll
- Record voiceover separately

**Organize assets:**
```
content/generated-videos/{{topic_slug}}/
├── raw-footage/
├── voiceover/
├── music/
├── b-roll/
└── assets-manifest.json
```

---

### Phase 8: Video Assembly & Validation (10-20 min)

**Execute editing plan:**
```bash
# Run FFmpeg commands from editing-plan.md
# Iterate until satisfied
```

**Validate final output:**
```bash
# Check specs
ffprobe -v error -show_entries format=duration,size -of default=nw=1 final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 final.mp4

# Requirements:
# - Duration: 3-90 seconds
# - Resolution: 1080x1920 (9:16)
# - Format: MP4 (H.264, AAC)
# - File size: <300MB
# - Audio: Stereo AAC
```

**Save validation report to:** `content/ready-to-publish/{{topic_slug}}/validation-report.md`

---

### Phase 9: Thumbnail Creation (5 min)

**Generate 3 thumbnail options:**
1. **Frame grab** — Best visual moment from video
2. **Text overlay** — Hook text on key frame
3. **Custom graphic** — Branded template with topic text

**Save to:** `content/ready-to-publish/{{topic_slug}}/thumbnails/`

---

### Phase 10: Final Package Assembly (5 min)

**Create final directory structure:**
```
content/ready-to-publish/{{topic_slug}}/
├── final-reel.mp4
├── script.md
├── caption.md
├── voiceover-script.md
├── shot-list.md
├── editing-plan.md
├── validation-report.md
├── thumbnails/
│   ├── thumb-1.jpg
│   ├── thumb-2.jpg
│   └── thumb-3.jpg
└── package-manifest.json
```

**Manifest.json:**
```json
{
  "topic": "{{topic}}",
  "slug": "{{topic_slug}}",
  "created": "{{timestamp}}",
  "duration_seconds": {{duration}},
  "file_size_mb": {{size}},
  "resolution": "1080x1920",
  "hashtags": ["#tag1", "#tag2"],
  "caption": "{{caption_text}}",
  "status": "ready-for-review",
  "approval_required": true
}
```

---

## Verification Checklist

Before marking complete:
- [ ] Script reads naturally at target duration
- [ ] Hook is compelling (tested mentally)
- [ ] Caption follows brand voice
- [ ] Hashtags validated (not banned, relevant)
- [ ] Video meets all Instagram specs
- [ ] File size < 300MB
- [ ] Audio clear, balanced
- [ ] Captions accurate (if burned in)
- [ ] Thumbnails eye-catching
- [ ] Package manifest complete
- [ ] Saved to `ready-to-publish/`

---

## Error Handling

| Failure Point | Recovery |
|---------------|----------|
| Research APIs fail | Use cached data, manual research |
| Script too long/short | Adjust beats, re-time |
| Video validation fails | Re-encode with correct params |
| FFmpeg errors | Check paths, codec support |
| Asset generation fails | Fall back to manual creation |
| Hashtag limit hit | Use cached hashtag IDs |

---

## MCP Commands Reference

```bash
# Research
instagram-mcp call discover_account --args '{"username": "TARGET"}'
instagram-mcp call compare_accounts --args '{"accounts": ["A", "B", "C"]}'
instagram-mcp call search_hashtag --args '{"hashtag": "TAG"}'
instagram-mcp call hashtag_top_media --args '{"hashtag": "TAG"}'
instagram-mcp call hashtag_recent_media --args '{"hashtag": "TAG"}'

# Pre-publish checks
instagram-mcp call get_publishing_limit --args '{"account": "YOUR_ACCOUNT"}'
instagram-mcp call token_status

# Publish (when approved)
instagram-mcp call create_container --args '{"account": "YOUR_ACCOUNT", "file": "PATH", "caption": "CAPTION"}' --confirm
# Wait for FINISHED status
instagram-mcp call get_container_status --args '{"container_id": "ID"}'
instagram-mcp call publish_container --args '{"container_id": "ID"}' --confirm
```