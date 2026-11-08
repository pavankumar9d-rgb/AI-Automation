# CHARACTER CONSISTENCY RULES — LÉA MOREAU

**Version:** 1.0  
**Date:** 2026-11-07  
**Status:** ENFORCED — NO EXCEPTIONS

---

## GOLDEN RULE

**One master identity image. One source of truth. Zero drift.**

Every single generated asset — every reference sheet, every expression, every outfit, every environment, every angle — must derive from and match the **approved master identity image**. No regeneration of the face. No "fresh take." No interpretation.

---

## NON-NEGOTIABLE LOCKS

| Element | Locked Value | Verification Method |
|---------|--------------|---------------------|
| **Face Geometry** | Exact facial proportions from master | Pixel overlay comparison |
| **Eye Color/Shape** | Hazel-brown `#7B8B6B`, almond, slight upturn | Color sample + landmark check |
| **Hair Color/Texture** | Chestnut `#4A3728`, Type 2B wave, mid-back | Strand-level consistency |
| **Skin Tone/Texture** | Warm medium-light `#D4A593`, pores, freckles | Texture analysis |
| **Freckle Pattern** | Specific map: nose bridge, upper cheeks | Pattern match |
| **Beauty Mark** | Left of chin, specific position | Coordinate lock |
| **Brow Asymmetry** | Left brow +1mm | Measurement |
| **Body Proportions** | Natural, realistic, consistent height | Skeletal landmark ratio |
| **Camera/Lens** | Per visual bible specs | EXIF/metadata check |

---

## GENERATION PROTOCOL

### **Step 1: Master Identity Selection (ONCE)**
1. Generate 4–6 candidate master portraits using master prompt
2. Human selects **ONE** as canonical
3. That image = `MASTER_IDENTITY.png` — **never overwritten without explicit approval**
4. All subsequent generations use this as reference (`-i MASTER_IDENTITY.png`)

### **Step 2: Reference Chaining**
- **Every generation** includes `-i MASTER_IDENTITY.png` (and previous approved refs)
- Use `reference_previous: true` equivalent: each new image references the last approved
- No generation starts from scratch

### **Step 3: Verification Gate**
Before accepting ANY output:
- [ ] Same person? (Face match)
- [ ] Same hair? (Color, texture, length, part)
- [ ] Same skin? (Tone, pores, freckles, beauty mark)
- [ ] Same proportions? (Body, face)
- [ ] Correct lighting per visual bible?
- [ ] Correct camera specs?
- [ ] No AI artifacts? (Extra fingers, melted fabric, plastic skin, symmetrical face)

**If ANY check fails → REJECT. Improve prompt. Regenerate.**

---

## PROHIBITED PATTERNS

| Pattern | Why It's Banned |
|---------|-----------------|
| "Generate a new face for this outfit" | Identity drift |
| "Make her look slightly different here" | Inconsistency |
| Using different models for different sheets | Model variance |
| Changing prompts between generations | Prompt drift |
| Accepting "close enough" | Compounding errors |
| Generating without master reference | Guaranteed drift |

---

## APPROVED WORKFLOW

```
MASTER_IDENTITY.png (approved)
    │
    ├─► CHARACTER_REFERENCE_SHEET (refs: MASTER)
    │       │
    │       ├─► EXPRESSION_SHEET (refs: MASTER + CHAR_SHEET)
    │       │
    │       ├─► WARDROBE_SHEET (refs: MASTER + CHAR_SHEET)
    │       │
    │       ├─► LIFESTYLE_ENVIRONMENTS (refs: MASTER + CHAR_SHEET)
    │       │
    │       └─► EXTRA_ANGLES (refs: MASTER + CHAR_SHEET)
    │
    └─► All future content (refs: MASTER + relevant sheet)
```

**Every arrow = reference image passed to generation.**

---

## MODEL CONSISTENCY

- **Primary Model:** `bytedance-seed/seedream-4.5` (photoreal control, seed support, reference images)
- **Fallback:** `google/gemini-3-pro-image` (high quality, reference support)
- **Draft/Iterate:** `google/gemini-3.1-flash-lite-image` (cheap, fast) — **ONLY for prompt tuning, NEVER for finals**

**Never mix models across a character's asset set.**

---

## SEED STRATEGY

- Use fixed seed for master identity generation
- Record seed in `GENERATION_WORKFLOW.md`
- For variations (expressions, outfits), use **seed + offset** (e.g., master_seed + 1, +2...) when model supports it
- Document all seeds used

---

## NAMING CONVENTION

```
LEA_MOREAU/
├── 01_MASTER_IDENTITY/
│   ├── MASTER_IDENTITY.png          ← THE ONE
│   ├── MASTER_IDENTITY_candidates/  ← rejected options
│   └── MASTER_PROMPT.txt
├── 02_CHARACTER_REFERENCE_SHEET/
│   ├── REF_SHEET_v1.png
│   ├── REF_SHEET_v2.png
│   └── REF_SHEET_FINAL.png
├── 03_EXPRESSION_SHEET/
│   ├── EXPR_neutral.png
│   ├── EXPR_soft_smile.png
│   ├── EXPR_full_laugh.png
│   ├── EXPR_focused.png
│   ├── EXPR_surprise.png
│   └── EXPRESSION_SHEET_FINAL.png
├── 04_WARDROBE/
│   ├── WARDROBE_casual.png
│   ├── WARDROBE_cafe.png
│   ├── WARDROBE_spring_walk.png
│   ├── WARDROBE_cozy_home.png
│   ├── WARDROBE_bakery.png
│   ├── WARDROBE_evening.png
│   └── WARDROBE_SHEET_FINAL.png
├── 05_LIFESTYLE_ENVIRONMENTS/
│   ├── ENV_paris_cafe.png
│   ├── ENV_paris_street.png
│   ├── ENV_bakery.png
│   ├── ENV_apartment_kitchen.png
│   ├── ENV_living_room.png
│   ├── ENV_flower_shop.png
│   ├── ENV_grocery.png
│   ├── ENV_bookshop.png
│   ├── ENV_park.png
│   ├── ENV_balcony.png
│   └── LIFESTYLE_SHEET_FINAL.png
├── 06_EXTRA_ANGLES/
│   ├── ANGLE_3q_left.png
│   ├── ANGLE_3q_right.png
│   ├── ANGLE_low.png
│   ├── ANGLE_high.png
│   ├── ANGLE_closeup_1.png
│   ├── ANGLE_closeup_2.png
│   └── EXTRA_ANGLES_SHEET.png
├── 07_GENERATION_PROMPTS/
│   ├── MASTER_PROMPT.txt
│   ├── REF_SHEET_PROMPT.txt
│   ├── EXPRESSION_PROMPTS.txt
│   ├── WARDROBE_PROMPTS.txt
│   ├── ENVIRONMENT_PROMPTS.txt
│   ├── EXTRA_ANGLES_PROMPTS.txt
│   └── SEEDS_LOG.txt
├── LEA_VISUAL_BIBLE.md
├── CHARACTER_CONSISTENCY_RULES.md  ← THIS FILE
└── GENERATION_WORKFLOW.md
```

---

## HUMAN APPROVAL CHECKPOINTS

**Mandatory human sign-off required at:**
1. **Master Identity Selection** — before any other generation
2. **Character Reference Sheet Final** — before expression/wardrobe/environment sheets
3. **Each Sheet Final** — before next sheet begins

**No autonomous continuation past checkpoints.**

---

## EMERGENCY RECOVERY

If drift detected in any approved asset:
1. **STOP** all generation
2. Identify drift source (prompt? model? reference chain broken?)
3. Regenerate from last verified asset + master reference
4. Re-verify entire chain

---

## VERSION HISTORY

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-11-07 | Initial rules established |

---

**REMEMBER:** A character that drifts is not a character — it's a series of different people wearing the same name. **Consistency IS the character.**