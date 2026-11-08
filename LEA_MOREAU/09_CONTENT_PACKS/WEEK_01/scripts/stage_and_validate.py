#!/usr/bin/env python3
"""
Léa Moreau — Instagram Content Staging & Validation Pipeline (Week 01)

Validates image formats, aspect ratios, slide ordering, captions, AI disclosures,
and hashtag compliance. Stages approved assets and generates STAGING_MANIFEST.json.

Safety Rules:
- Default mode is DRY-RUN.
- No network requests, API uploads, or publishing are performed in this script.
- Never prints secrets, credentials, or tokens.
"""

import os
import sys
import json
import shutil
import re
from pathlib import Path
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
WEEK_01_DIR = SCRIPT_DIR.parent
CAROUSEL_01_DIR = WEEK_01_DIR / "CAROUSEL_01_SLOW_PARIS_MORNING"
STAGING_DIR = WEEK_01_DIR / "STAGING"
MANIFEST_PATH = WEEK_01_DIR / "STAGING_MANIFEST.json"

REQUIRED_SLIDES = [
    "SLIDE_01_MORNING_COFFEE.png",
    "SLIDE_02_OUTFIT_DETAILS.png",
    "SLIDE_03_PARIS_STREET.png"
]

MANDATORY_AI_DISCLOSURE = "Fictional AI creator — Léa Moreau ✨"
MIN_HASHTAGS = 5
MAX_HASHTAGS = 15
TARGET_ASPECT_RATIO = 4.0 / 5.0  # 0.8
ASPECT_RATIO_TOLERANCE = 0.03    # 0.77 to 0.83


def validate_image(image_path: Path):
    """Validates an image file's existence, format, and aspect ratio."""
    if not image_path.exists():
        return False, f"Missing image file: {image_path.name}"
    
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            img_format = img.format
            ratio = width / height
            
            # Check ratio
            if abs(ratio - TARGET_ASPECT_RATIO) > ASPECT_RATIO_TOLERANCE:
                return False, f"Invalid aspect ratio {ratio:.4f} (expected ~0.80 for 4:5): {image_path.name}"
            
            # Check minimum resolution
            if width < 800 or height < 1000:
                return False, f"Resolution too low ({width}x{height}): {image_path.name}"
            
            return True, {
                "filename": image_path.name,
                "width": width,
                "height": height,
                "format": img_format,
                "aspect_ratio": round(ratio, 4),
                "valid": True
            }
    except Exception as e:
        return False, f"Corrupted or unreadable image {image_path.name}: {str(e)}"


def validate_caption(caption_path: Path):
    """Validates caption text, AI disclosure, and hashtag count."""
    if not caption_path.exists():
        return False, f"Missing caption file: {caption_path.name}", None
    
    try:
        text = caption_path.read_text(encoding="utf-8")
        
        # Check AI disclosure
        has_disclosure = MANDATORY_AI_DISCLOSURE in text
        if not has_disclosure:
            return False, f"Missing mandatory AI disclosure: '{MANDATORY_AI_DISCLOSURE}'", None
        
        # Count hashtags
        hashtags = re.findall(r"#\w+", text)
        if len(hashtags) < MIN_HASHTAGS or len(hashtags) > MAX_HASHTAGS:
            return False, f"Invalid hashtag count ({len(hashtags)}). Must be between {MIN_HASHTAGS} and {MAX_HASHTAGS}.", None
        
        return True, "Caption passed all validation checks.", {
            "char_count": len(text),
            "hashtag_count": len(hashtags),
            "hashtags": hashtags,
            "has_ai_disclosure": True,
            "raw_text": text.strip()
        }
    except Exception as e:
        return False, f"Error reading caption: {str(e)}", None


def run_pipeline(dry_run: bool = True):
    print("=" * 65)
    print(f"LÉA MOREAU — CONTENT STAGING & VALIDATION PIPELINE")
    print(f"Mode: {'DRY-RUN (Simulating validation only)' if dry_run else 'APPLY (Staging approved files)'}")
    print(f"Directory: {WEEK_01_DIR}")
    print("=" * 65)
    
    overall_valid = True
    validated_slides = []
    
    # 1. Validate Carousel Slides
    print("\n[1/3] Validating Carousel Media Files...")
    for idx, slide_name in enumerate(REQUIRED_SLIDES, start=1):
        slide_path = CAROUSEL_01_DIR / slide_name
        valid, info = validate_image(slide_path)
        if valid:
            info["slide_index"] = idx
            validated_slides.append(info)
            print(f"  ✓ Slide {idx} OK: {slide_name} ({info['width']}x{info['height']}, ratio {info['aspect_ratio']})")
        else:
            overall_valid = False
            print(f"  ✗ Slide {idx} FAILED: {info}")
            
    # 2. Validate Caption
    print("\n[2/3] Validating Caption & Metadata...")
    caption_path = CAROUSEL_01_DIR / "CAROUSEL_CAPTION.md"
    cap_valid, cap_msg, cap_meta = validate_caption(caption_path)
    if cap_valid:
        print(f"  ✓ Caption OK: {cap_meta['char_count']} chars, {cap_meta['hashtag_count']} hashtags, AI disclosure present.")
    else:
        overall_valid = False
        print(f"  ✗ Caption FAILED: {cap_msg}")

    # 3. Staging and Manifest Generation
    print("\n[3/3] Manifest & Staging Execution...")
    manifest_data = {
        "pack_name": "WEEK_01",
        "post_id": "CAROUSEL_01_SLOW_PARIS_MORNING",
        "format": "CAROUSEL",
        "destination_account": "@pavan_create",
        "validation_passed": overall_valid,
        "mode": "DRY_RUN" if dry_run else "STAGED",
        "slides": validated_slides,
        "caption_metadata": cap_meta if cap_valid else None,
        "staging_directory": str(STAGING_DIR),
        "publishing_status": "PENDING_USER_APPROVAL",
        "safeguards": {
            "auto_publish_enabled": False,
            "manual_review_required": True
        }
    }
    
    if not overall_valid:
        print("\n❌ VALIDATION FAILED! Staging aborted. Please resolve the errors above.")
        return False

    if dry_run:
        print("  ✓ DRY-RUN SUCCESSFUL: All assets and metadata meet 100% quality criteria.")
        print("  ℹ️ Run with '--stage' to physically copy assets into STAGING directory.")
    else:
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        for s in validated_slides:
            src = CAROUSEL_01_DIR / s["filename"]
            dst = STAGING_DIR / s["filename"]
            shutil.copy2(src, dst)
            print(f"  ✓ Staged: {s['filename']} -> STAGING/")
            
        MANIFEST_PATH.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✓ Manifest written: {MANIFEST_PATH.name}")
        print("\n🎉 ALL ASSETS SUCCESSFULLY VALIDATED & STAGED!")
        
    return True


if __name__ == "__main__":
    is_apply = "--stage" in sys.argv or "--apply" in sys.argv
    success = run_pipeline(dry_run=not is_apply)
    sys.exit(0 if success else 1)

