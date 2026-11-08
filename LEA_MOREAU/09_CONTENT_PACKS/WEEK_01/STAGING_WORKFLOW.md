# Léa Moreau — Instagram Staging & Publishing Workflow Architecture
**Module:** Content Automation & Staging (Week 01)  
**Destination Account:** `@pavan_create` (Instagram Creator Account)  
**Safety Protocol:** Manual Gate Enforced (No automatic publishing permitted)

---

## 1. Overview & Workflow Stages

The content production and publishing pipeline operates across four strictly decoupled tiers:

```
[Tier 1: Generation & Creative Pack]
  ├── Visual Assets (4:5 Images / 9:16 Reels)
  ├── Captions with Mandatory AI Disclosure
  └── Quality Assurance (QA passed & identity locked)
               │
               ▼
[Tier 2: Validation & Staging Pipeline]
  ├── scripts/stage_and_validate.py (Dry-run by default)
  ├── Image aspect ratio & resolution verification
  ├── Disclosure & hashtag count checks
  └── Output: STAGING_MANIFEST.json & STAGING/ directory
               │
               ▼
[Tier 3: Temporary Hosting & Container Creation]
  ├── Local HTTP server + ephemeral Cloudflare Quick Tunnel
  ├── Creation of individual child item containers (is_carousel_item=true)
  └── Creation of parent CAROUSEL container with caption & hashtags
               │
               ▼
[Tier 4: Gated Publishing Execution]
  ├── User explicitly reviews images, order, and caption
  ├── User enters explicit confirmation flag
  └── Call to Graph API `me/media_publish`
```

---

## 2. Validation & Staging Standards (`scripts/stage_and_validate.py`)

Before any asset can be considered staged for publishing, it must satisfy all deterministic rules:
1. **Aspect Ratio Enforcement:** Exactly 4:5 vertical portrait ($819 \times 1024$ or $1080 \times 1350$). Tolerance: $\pm 3\%$.
2. **File Integrity:** Valid uncorrupted PNG or JPEG format, minimum 800px width.
3. **Mandatory AI Disclosure:** Exact string required:
   ```
   Fictional AI creator — Léa Moreau ✨
   ```
4. **Hashtag Boundary:** Minimum 5 hashtags, maximum 15 hashtags.
5. **Dry-Run Default:** Executing `python scripts/stage_and_validate.py` operates in read-only dry-run mode. Staging only occurs with explicit `--stage` argument.
6. **Zero Credential Exposure:** Script never references `.env` values or tokens, and produces a sanitized `STAGING_MANIFEST.json`.

---

## 3. Instagram Graph API Carousel Workflow Reference

When the user gives explicit written approval to publish Carousel 01, the automation follows Meta's standard Graph API carousel procedure:

### Step 3.1: Host Staged Assets via Temporary Cloudflare Tunnel
Meta servers require public, directly accessible HTTPS image URLs to download media:
```bash
# Terminal 1: Spin up local static server from STAGING directory
python -m http.server 8000 --directory ./STAGING

# Terminal 2: Spin up Cloudflare ephemeral quick tunnel
cloudflared tunnel --url http://localhost:8000
```

### Step 3.2: Create Item Media Containers (Children)
For each slide in the carousel, create a container with `is_carousel_item=true`:
```http
POST https://graph.facebook.com/v21.0/{ig_user_id}/media
  image_url=<PUBLIC_CLOUDFLARE_URL>/SLIDE_01_MORNING_COFFEE.png
  is_carousel_item=true
  access_token={PAGE_ACCESS_TOKEN}
```
*Repeat for Slide 2 and Slide 3 to retrieve their respective container IDs ($C_1, C_2, C_3$).*

### Step 3.3: Create Carousel Container (Parent)
Create the parent container grouping all children with the final caption:
```http
POST https://graph.facebook.com/v21.0/{ig_user_id}/media
  media_type=CAROUSEL
  children={C1},{C2},{C3}
  caption={FULL_CAPTION_TEXT}
  access_token={PAGE_ACCESS_TOKEN}
```
*Returns Parent Container ID ($C_{parent}$).*

### Step 3.4: Final Publishing Gate (`me/media_publish`)
**CRITICAL:** Only executed after explicit user verification:
```http
POST https://graph.facebook.com/v21.0/{ig_user_id}/media_publish
  creation_id={C_parent}
  access_token={PAGE_ACCESS_TOKEN}
```

---

## 4. Current Operational Safeguards
- **Live Publishing:** **CURRENTLY BLOCKED / AWAITING USER APPROVAL**.
- **Test Post Status:** Step 1 test post (`https://www.instagram.com/p/DfefUfOj92j/`) remains live and verified.
- **Account Settings:** Live profile bio, profile picture, and username are untouched until explicit Phase 5 signoff.

