# GENERATION WORKFLOW — LÉA MOREAU

**Version:** 1.0  
**Date:** 2026-11-07  
**Status:** ACTIVE PROTOCOL

---

## TOOLCHAIN

### **Primary: flow-mcp (Google Flow via Chrome)**
- **Path:** `/tmp/flow-mcp/dist/index.js`
- **MCP Server Name:** `flow-mcp`
- **Capabilities:** Character creation, reference images, batch generation, agent mode
- **Auth:** Requires Google account signed into Chrome profile
- **Cost:** Free for images (Nano Banana), credits for video

### **Fallback: generate-image (OpenRouter API)**
- **Skill:** `generate-image`
- **Models:** `bytedance-seed/seedream-4.5` (primary), `google/gemini-3-pro-image` (fallback)
- **Requires:** `OPENROUTER_API_KEY` in environment
- **Cost:** Per image (Seedream ~$0.04, Gemini 3 Pro ~$0.08–$0.32)

---

## PHASE 0: ENVIRONMENT SETUP

### **flow-mcp Setup**
```bash
# 1. Ensure Chrome is installed
# 2. Create dedicated Chrome profile for Flow
mkdir -p ~/.flow-mcp/chrome-profile

# 3. Run flow-mcp login to authenticate
cd /tmp/flow-mcp && node dist/login.js

# 4. Verify connection
node dist/index.js  # Should start MCP server

# 5. Register in Claude Code
# Add to ~/.claude/mcp_servers.json:
# {
#   "mcpServers": {
#     "flow-mcp": {
#       "command": "node",
#       "args": ["/tmp/flow-mcp/dist/index.js"],
#       "env": { "FLOW_MCP_OUTPUT": "~/flow-mcp-out" }
#     }
#   }
# }
```

### **generate-image Setup**
```bash
# 1. Get OpenRouter API key: https://openrouter.ai/keys
# 2. Set in environment:
export OPENROUTER_API_KEY="sk-or-..."

# 3. Or create .env in project:
echo "OPENROUTER_API_KEY=sk-or-..." > .env

# 4. Test:
cd ~/.claude/skills/generate-image && python scripts/generate_image.py "test" --dry-run
```

---

## PHASE 1: MASTER IDENTITY GENERATION

### **Prompt File:** `07_GENERATION_PROMPTS/MASTER_PROMPT.txt`

```
Photorealistic portrait of Léa Moreau, 25-year-old French woman, chestnut-brown wavy hair center-parted falling to mid-back, hazel-brown eyes with green-gold flecks, warm medium-light skin with visible pores and light freckles across nose and cheeks, soft oval face with gentle jawline, natural lips, slight left-brow asymmetry, small beauty mark left of chin. Wearing cream cable-knit merino sweater, soft window light from camera-left (north-facing window), large rectangular catchlights in eyes, 85mm lens, f/1.8, ISO 400, full-frame, Kodak Portra 400 color science, sharp focus on nearest eye, creamy bokeh background, warm white neutral wall. No makeup look, no filters, no CGI, no 3D render artifacts. Aspect ratio 4:5.
```

### **Generation Command (generate-image fallback):**
```bash
cd ~/.claude/skills/generate-image
python scripts/generate_image.py \
  "$(cat ../../../../Instagram-AI-Automation/LEA_MOREAU/07_GENERATION_PROMPTS/MASTER_PROMPT.txt)" \
  -m bytedance-seed/seedream-4.5 \
  --aspect-ratio 4:5 \
  --resolution 2K \
  --seed 42 \
  -o ../../../../Instagram-AI-Automation/LEA_MOREAU/01_MASTER_IDENTITY/MASTER_IDENTITY_candidates/seed42.png
```

### **Generate Multiple Candidates:**
```bash
for seed in 42 123 456 789 999; do
  python scripts/generate_image.py \
    "$(cat MASTER_PROMPT.txt)" \
    -m bytedance-seed/seedream-4.5 \
    --aspect-ratio 4:5 \
    --resolution 2K \
    --seed $seed \
    -o 01_MASTER_IDENTITY/MASTER_IDENTITY_candidates/seed${seed}.png
done
```

### **Selection Protocol:**
1. Review all candidates
2. Human selects ONE → rename to `MASTER_IDENTITY.png` in `01_MASTER_IDENTITY/`
3. Record selected seed in `SEEDS_LOG.txt`
4. **Lock:** This file is now the single source of truth

---

## PHASE 2: CHARACTER REFERENCE SHEET

### **Prompt:** `07_GENERATION_PROMPTS/REF_SHEET_PROMPT.txt`

```
Professional character reference sheet for Léa Moreau, single cohesive layout, photorealistic photography. Same woman in all panels — chestnut-brown wavy hair center-parted to mid-back, hazel-brown eyes, warm medium-light skin with pores and freckles, soft oval face, beauty mark left of chin.

TOP ROW — Four full-body views (35mm equivalent, f/4, full-frame):
1. Front-facing, relaxed stance, weight evenly distributed, arms natural at sides
2. Three-quarter turn left, head turned toward camera, natural contrapposto
3. Full left-side profile, arms relaxed, head forward
4. Back view, head turned slightly over right shoulder, hair falling naturally

BOTTOM ROW — Three close-up portraits (85mm equivalent, f/1.8):
1. Front-facing portrait, neutral expression, eye contact
2. Three-quarter portrait, head tilted slightly, soft gaze
3. Left-side profile portrait, jawline visible, ear visible

ALL PANELS: Soft neutral window light (north-facing), warm white background (#FAF8F5), consistent lighting scale and eyeline across all seven views. Same cream cable-knit sweater and mid-wash jeans. No text, no labels, no grid lines. Kodak Portra 400 color science. Aspect ratio 3:2 per panel, sheet layout 4×2 grid.
```

### **Generation (using master as reference):**
```bash
# flow-mcp approach (preferred):
# flow_generate with reference_images: ["asset:MASTER_IDENTITY"]

# generate-image fallback:
python scripts/generate_image.py \
  "$(cat REF_SHEET_PROMPT.txt)" \
  -m bytedance-seed/seedream-4.5 \
  --aspect-ratio 3:2 \
  --resolution 4K \
  -i ../../../../Instagram-AI-Automation/LEA_MOREAU/01_MASTER_IDENTITY/MASTER_IDENTITY.png \
  -o 02_CHARACTER_REFERENCE_SHEET/REF_SHEET_v1.png
```

---

## PHASE 3: EXPRESSION SHEET

### **Prompts:** `07_GENERATION_PROMPTS/EXPRESSION_PROMPTS.txt`

Each expression uses same base + expression modifier:

**Base:** `Photorealistic close-up portrait of Léa Moreau, 25, chestnut-brown wavy hair center-parted, hazel-brown eyes, warm medium-light skin with pores and freckles, soft oval face, beauty mark left of chin. 85mm lens, f/1.8, soft north window light, large rectangular catchlights, Kodak Portra 400, sharp eye focus. Aspect ratio 4:5.`

| Expression | Modifier | Output |
|------------|----------|--------|
| Neutral | `Neutral relaxed face, soft gaze, lips closed, natural micro-expression` | `EXPR_neutral.png` |
| Soft Smile | `Genuine soft smile, corners of mouth lifted, eyes slightly crinkled (Duchenne), warm and approachable` | `EXPR_soft_smile.png` |
| Full Laugh | `Natural full laugh, head tilted back slightly, mouth open showing teeth, eyes crinkled with joy, hair moving` | `EXPR_full_laugh.png` |
| Focused | `Calm serious focus, slight brow furrow, direct gaze, lips pressed gently, thinking expression` | `EXPR_focused.png` |
| Mild Surprise | `Gentle surprise, eyebrows raised slightly, eyes widened, mouth slightly parted, natural reaction` | `EXPR_surprise.png` |

### **Generation:**
```bash
for expr in neutral soft_smile full_laugh focused surprise; do
  python scripts/generate_image.py \
    "$(cat EXPRESSION_PROMPTS.txt | grep -A1 "^$expr:" | tail -1)" \
    -m bytedance-seed/seedream-4.5 \
    --aspect-ratio 4:5 \
    --resolution 2K \
    -i ../../../../Instagram-AI-Automation/LEA_MOREAU/01_MASTER_IDENTITY/MASTER_IDENTITY.png \
    -i ../../../../Instagram-AI-Automation/LEA_MOREAU/02_CHARACTER_REFERENCE_SHEET/REF_SHEET_FINAL.png \
    -o 03_EXPRESSION_SHEET/EXPR_${expr}.png
done
```

---

## PHASE 4: WARDROBE SHEET

### **Prompts:** `07_GENERATION_PROMPTS/WARDROBE_PROMPTS.txt`

Each outfit: full-body (35mm, f/4) + upper-body detail (50mm, f/2.8)

| Outfit | Description |
|--------|-------------|
| Casual Everyday | Cream cable-knit sweater, mid-wash straight jeans, white leather sneakers, terracotta tote |
| Paris Café | Oversized beige trench coat, cream ribbed turtleneck, dark wash straight jeans, brown leather loafers, silk scarf (sage green) |
| Spring Walk | Light denim jacket, white cotton tee, midi floral skirt (cream/terracotta/sage), white canvas sneakers, crossbody bag |
| Cozy Home | Oversized oatmeal cardigan, matching knit tank, soft gray joggers, barefoot or wool socks, messy bun |
| Bakery/Grocery | Camel wool wrap coat, chunky cream turtleneck, corduroy pants (warm brown), leather ankle boots, canvas market tote |
| Elegant Evening | Silk charmeuse blouse (champagne), high-waisted wide-leg trousers (black), minimal gold jewelry, pointed flats |

### **Generation:** Same pattern — master + reference sheet as `-i` inputs

---

## PHASE 5: LIFESTYLE ENVIRONMENTS

### **Prompts:** `07_GENERATION_PROMPTS/ENVIRONMENT_PROMPTS.txt`

Each environment: environmental portrait (35mm or 24mm, f/2.8–f/4), character placed naturally in scene

| Environment | Lighting Schema | Key Details |
|-------------|----------------|-------------|
| Paris Café | Tertiary (mixed) | Corner table, espresso, croissant, Haussmann windows, street view |
| Paris Street | Secondary (golden hour) | Walking on boulevard, Haussmann facade, dappled tree light |
| French Bakery | Tertiary | Counter with baguettes, pastries, flour dust, warm ovens |
| Apartment Kitchen | Primary (window) | Morning coffee, marble counter, herbs, window over sink |
| Living Room | Tertiary (evening) | Reading, floor lamp, books, textured throw, plants |
| Flower Shop | Primary | Surrounded by buckets, selecting peonies, natural light |
| Grocery Store | Tertiary (fluorescent + window) | Market basket, produce aisle, reaching for fruit |
| Bookshop | Tertiary | Aisle, pulling book, ladder, warm lamps, stacked tables |
| Paris Park | Secondary | Sitting on bench, journal, plane trees, gravel path |
| Balcony | Secondary/Primary | Overlooking street, morning coffee, wrought iron, cityscape |

---

## PHASE 6: EXTRA ANGLES

### **Prompts:** `07_GENERATION_PROMPTS/EXTRA_ANGLES_PROMPTS.txt`

| Angle | Spec |
|-------|------|
| Three-quarter Left | 35mm, f/2.8, slight turn, weight on back foot |
| Three-quarter Right | 35mm, f/2.8, mirror of left |
| Slight Low Angle | 50mm, f/2.2, camera 15° up, empowering but natural |
| Slight High Angle | 50mm, f/2.2, camera 15° down, approachable |
| Tight Close-up 1 | 105mm macro, f/2.8, eyes/nose/mouth only, pores visible |
| Tight Close-up 2 | 105mm macro, f/2.8, eye detail, lashes, iris texture |

---

## SEED LOG TEMPLATE

```
MASTER_IDENTITY: seed=42 (SELECTED)
CHARACTER_REF_SHEET: seed=42 (ref_previous)
EXPR_neutral: seed=43
EXPR_soft_smile: seed=44
EXPR_full_laugh: seed=45
EXPR_focused: seed=46
EXPR_surprise: seed=47
WARDROBE_casual: seed=48
WARDROBE_cafe: seed=49
WARDROBE_spring: seed=50
WARDROBE_home: seed=51
WARDROBE_bakery: seed=52
WARDROBE_evening: seed=53
ENV_cafe: seed=54
ENV_street: seed=55
ENV_bakery: seed=56
ENV_kitchen: seed=57
ENV_living: seed=58
ENV_flower: seed=59
ENV_grocery: seed=60
ENV_bookshop: seed=61
ENV_park: seed=62
ENV_balcony: seed=63
ANGLE_3q_left: seed=64
ANGLE_3q_right: seed=65
ANGLE_low: seed=66
ANGLE_high: seed=67
ANGLE_closeup1: seed=68
ANGLE_closeup2: seed=69
```

---

## VERIFICATION CHECKLIST (per asset)

- [ ] Face matches master (overlay test)
- [ ] Hair identical (color, texture, part, length)
- [ ] Skin identical (tone, pores, freckles, beauty mark)
- [ ] Eyes identical (color, shape, asymmetry)
- [ ] Proportions correct (body, face)
- [ ] Lighting matches visual bible schema
- [ ] Camera specs match (focal, aperture, DOF)
- [ ] No AI artifacts (hands, symmetry, plastic skin, melted fabric)
- [ ] Color palette matches swatches
- [ ] Clothing behaves as real fabric

---

## HANDOFF TO PHASE 4 (CONTENT PIPELINE)

Once all sheets approved:
1. Master identity + all reference sheets = **Character Asset Package**
2. Package used for: content calendar generation, Reel storyboards, Story assets, Carousel designs
3. All Phase 4+ generation uses `MASTER_IDENTITY.png` + relevant sheet as references

---

## TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| Drift detected | Regenerate from last verified + master |
| Model inconsistency | Lock to single model (Seedream 4.5) |
| Lighting wrong | Explicit lighting schema in prompt |
| Hands distorted | Add "hands relaxed at sides" or hide hands |
| Plastic skin | Add "visible pores, skin texture, film grain" |
| Symmetrical face | Add "natural asymmetry, left brow slightly higher" |
| Wrong eye color | Add "hazel-brown with green-gold flecks #7B8B6B" |