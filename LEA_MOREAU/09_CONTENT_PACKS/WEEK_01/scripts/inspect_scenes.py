import subprocess
import os

out_dir = r"C:\Users\saipa\Instagram-AI-Automation\LEA_MOREAU\09_CONTENT_PACKS\WEEK_01\scripts\frame_checks"
os.makedirs(out_dir, exist_ok=True)

for sc in ["scene-05.mp4", "scene-06.mp4", "scene-07.mp4"]:
    vpath = os.path.join(r"C:\Users\saipa\flow-mcp-out\Lea_Campaign_W01", sc)
    sc_name = os.path.splitext(sc)[0]
    # Extract 1 frame per second
    out_pattern = os.path.join(out_dir, f"{sc_name}_%02d.jpg")
    cmd = ["ffmpeg", "-y", "-i", vpath, "-vf", "fps=1", out_pattern]
    subprocess.run(cmd, capture_output=True)

frames = sorted(os.listdir(out_dir))
print(f"Extracted {len(frames)} frames across the 3 scenes.")
for f in frames:
    print(f)

