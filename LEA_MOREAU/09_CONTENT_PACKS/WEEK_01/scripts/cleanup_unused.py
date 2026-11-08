import os
import shutil

base_dir = r"C:\Users\saipa\Instagram-AI-Automation\LEA_MOREAU\09_CONTENT_PACKS\WEEK_01"

# Unused files and folders to remove
remove_targets = [
    # Redundant carousel test directory
    os.path.join(base_dir, "CAROUSEL_01_SLOW_PARIS_MORNING"),
    # Staging slides
    os.path.join(base_dir, "STAGING", "SLIDE_01_MORNING_COFFEE.png"),
    os.path.join(base_dir, "STAGING", "SLIDE_02_OUTFIT_DETAILS.png"),
    os.path.join(base_dir, "STAGING", "SLIDE_03_PARIS_STREET.png"),
    # Unused slides in POST_02 and POST_04
    os.path.join(base_dir, "POSTS", "POST_01_CAFE_MORNING", "POST_01_CAFE_MORNING.png"),
    os.path.join(base_dir, "POSTS", "POST_02_PARISIAN_STYLE", "SLIDE_01.png"),
    os.path.join(base_dir, "POSTS", "POST_02_PARISIAN_STYLE", "SLIDE_02.png"),
    os.path.join(base_dir, "POSTS", "POST_02_PARISIAN_STYLE", "SLIDE_03.png"),
    os.path.join(base_dir, "POSTS", "POST_03_COZY_APARTMENT", "POST_03_COZY_APARTMENT.png"),
    os.path.join(base_dir, "POSTS", "POST_04_SLOW_SUNDAY", "SLIDE_01.png"),
    os.path.join(base_dir, "POSTS", "POST_04_SLOW_SUNDAY", "SLIDE_02.png"),
    os.path.join(base_dir, "POSTS", "POST_04_SLOW_SUNDAY", "SLIDE_03.png"),
]

deleted = []
for target in remove_targets:
    if os.path.exists(target):
        if os.path.isdir(target):
            shutil.rmtree(target)
            deleted.append(f"DIR: {target}")
        else:
            os.remove(target)
            deleted.append(f"FILE: {target}")

print("Cleaned targets:")
for d in deleted:
    print(" - Removed:", d)

