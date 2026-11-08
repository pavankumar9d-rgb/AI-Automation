import os
import shutil
import subprocess

reels_dir = r"C:\Users\saipa\Instagram-AI-Automation\LEA_MOREAU\09_CONTENT_PACKS\WEEK_01\REELS"
raw_flow_dir = r"C:\Users\saipa\flow-mcp-out\Lea_Campaign_W01"

reel_mappings = [
    {
        "id": "REEL_01_MORNING_COFFEE",
        "video": os.path.join(raw_flow_dir, "scene-05.mp4"),
        "audio": r"C:\Users\saipa\Downloads\reel 1.mp3",
        "folder": os.path.join(reels_dir, "REEL_01_MORNING_COFFEE")
    },
    {
        "id": "REEL_02_PARIS_DISCOVERY",
        "video": os.path.join(raw_flow_dir, "scene-06.mp4"),
        "audio": r"C:\Users\saipa\Downloads\reel 2.mp3",
        "folder": os.path.join(reels_dir, "REEL_02_PARIS_DISCOVERY")
    },
    {
        "id": "REEL_03_BAKERY_RUN",
        "video": os.path.join(raw_flow_dir, "scene-07.mp4"),
        "audio": r"C:\Users\saipa\Downloads\reel 3.mp3",
        "folder": os.path.join(reels_dir, "REEL_03_BAKERY_RUN")
    }
]

for item in reel_mappings:
    target_folder = item["folder"]
    os.makedirs(target_folder, exist_ok=True)
    
    # 1. Copy user audio to target folder
    target_audio = os.path.join(target_folder, "VOICEOVER_PEONY.mp3")
    shutil.copy2(item["audio"], target_audio)
    print(f"Copied {item['audio']} to {target_audio}")
    
    # 2. Extract clean cover from video at 1.0s
    cover_path = os.path.join(target_folder, "COVER.png")
    cmd_cover = [
        "ffmpeg", "-y", "-ss", "00:00:01.000", "-i", item["video"],
        "-vframes", "1", "-vf", "scale=1080:1920:flags=lanczos", cover_path
    ]
    subprocess.run(cmd_cover, capture_output=True)
    print(f"Generated cover: {cover_path}")
    
    # 3. Create synchronized video with voiceover
    # Crop bottom watermark (crop=in_w:in_h-96:0:0, scale=1080:1920) and mux audio
    output_video = os.path.join(target_folder, "REEL_VIDEO_CLEAN.mp4")
    
    # Audio starts at 0.0s matching mouth movements, fades out cleanly at end of video
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", item["video"],
        "-i", target_audio,
        "-filter_complex",
        "[0:v]crop=in_w:in_h-96:0:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5:5:5:0.0[v];[1:a]afade=t=out:st=7.5:d=0.5[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video
    ]
    res = subprocess.run(cmd_mux, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Successfully rendered: {output_video} ({os.path.getsize(output_video)} bytes)")
    else:
        print(f"Render failed for {item['id']}: {res.stderr[:200]}")

