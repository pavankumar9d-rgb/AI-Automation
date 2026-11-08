import os
import cv2
import numpy as np
from PIL import Image

posts_base = r"C:\Users\saipa\Instagram-AI-Automation\LEA_MOREAU\09_CONTENT_PACKS\WEEK_01\POSTS"
brain_base = r"C:\Users\saipa\.gemini\antigravity\brain\db47c8a7-6fa9-4ed7-809e-118bd3caefdd"

processing_jobs = [
    # Post 01
    {
        "post_folder": os.path.join(posts_base, "POST_01_CAFE_MORNING"),
        "slide_01_existing": os.path.join(posts_base, "POST_01_CAFE_MORNING", "IMAGE_01_CLEAN.png"),
        "slide_02_raw": os.path.join(brain_base, "post01_slide02_cafe_morning_1794151602770.jpg"),
        "slide_03_raw": os.path.join(brain_base, "lea_post01_slide03_cafe_morning_1794151646374.jpg")
    },
    # Post 02
    {
        "post_folder": os.path.join(posts_base, "POST_02_PARISIAN_STYLE"),
        "slide_01_existing": os.path.join(posts_base, "POST_02_PARISIAN_STYLE", "IMAGE_01_CLEAN.png"),
        "slide_02_raw": os.path.join(brain_base, "parisian_style_slide_02_1794151540204.jpg"),
        "slide_03_raw": os.path.join(brain_base, "post02_slide03_parisian_street_style_1794151604286.jpg")
    },
    # Post 03
    {
        "post_folder": os.path.join(posts_base, "POST_03_COZY_APARTMENT"),
        "slide_01_existing": os.path.join(posts_base, "POST_03_COZY_APARTMENT", "IMAGE_01_CLEAN.png"),
        "slide_02_raw": os.path.join(brain_base, "post03_slide02_parisian_living_room_1794151616551.jpg"),
        "slide_03_raw": os.path.join(brain_base, "lea_post03_slide03_1794151625099.jpg")
    },
    # Post 04
    {
        "post_folder": os.path.join(posts_base, "POST_04_SLOW_SUNDAY"),
        "slide_01_existing": os.path.join(posts_base, "POST_04_SLOW_SUNDAY", "IMAGE_01_CLEAN.png"),
        "slide_02_raw": os.path.join(brain_base, "post04_slide02_flower_market_1794151611851.jpg"),
        "slide_03_raw": os.path.join(brain_base, "post04_slide03_marais_flowers_1794151651012.jpg")
    }
]

def enhance_and_crop(raw_path, out_path, target_w=1080, target_h=1350):
    # Load with PIL to strip all metadata
    with Image.open(raw_path) as pil_img:
        # Convert to RGB clean image without any EXIF or C2PA
        clean_img = Image.new("RGB", pil_img.size)
        clean_img.paste(pil_img)
    
    cv_img = cv2.cvtColor(np.array(clean_img), cv2.COLOR_RGB2BGR)
    h, w = cv_img.shape[:2]
    
    # Crop to 4:5 aspect ratio
    target_ratio = 4.0 / 5.0
    current_ratio = w / h
    
    if current_ratio > target_ratio:
        # Crop sides
        new_w = int(h * target_ratio)
        start_x = (w - new_w) // 2
        cv_img = cv_img[:, start_x:start_x + new_w]
    else:
        # Crop top/bottom
        new_h = int(w / target_ratio)
        start_y = (h - new_h) // 2
        cv_img = cv_img[start_y:start_y + new_h, :]
        
    # Resize to exactly 1080x1350 with high-quality Lanczos-4
    resized = cv2.resize(cv_img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    
    # Bilateral filter to smooth AI plastic artifacts while preserving sharp edges
    smoothed = cv2.bilateralFilter(resized, d=5, sigmaColor=35, sigmaSpace=35)
    
    # CLAHE on L channel for vibrant micro-contrast
    lab = cv2.cvtColor(smoothed, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l_enhanced, a, b]), cv2.COLOR_LAB2BGR)
    
    # Unsharp mask for crisp high-end details
    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 1.5)
    unsharp = cv2.addWeighted(enhanced, 1.25, gaussian, -0.25, 0)
    
    # Add subtle organic film grain (sigma = 0.9) to mask synthetic AI smoothing
    np.random.seed(42)
    noise = np.random.normal(0, 0.9, unsharp.shape).astype(np.float32)
    noisy = np.clip(unsharp.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    # Save clean PNG (lossless, zero metadata)
    cv2.imwrite(out_path, noisy, [cv2.IMWRITE_PNG_COMPRESSION, 4])
    print(f"Processed: {out_path} ({os.path.getsize(out_path)} bytes, 1080x1350)")

for job in processing_jobs:
    folder = job["post_folder"]
    
    # Slide 01: copy existing clean image to SLIDE_01.png
    slide_01_dest = os.path.join(folder, "SLIDE_01.png")
    if not os.path.exists(slide_01_dest) and os.path.exists(job["slide_01_existing"]):
        import shutil
        shutil.copy2(job["slide_01_existing"], slide_01_dest)
        print(f"Set Slide 01: {slide_01_dest}")
    elif os.path.exists(slide_01_dest):
        print(f"Slide 01 already exists: {slide_01_dest}")
        
    # Slide 02
    slide_02_dest = os.path.join(folder, "SLIDE_02.png")
    enhance_and_crop(job["slide_02_raw"], slide_02_dest)
    
    # Slide 03
    slide_03_dest = os.path.join(folder, "SLIDE_03.png")
    enhance_and_crop(job["slide_03_raw"], slide_03_dest)

