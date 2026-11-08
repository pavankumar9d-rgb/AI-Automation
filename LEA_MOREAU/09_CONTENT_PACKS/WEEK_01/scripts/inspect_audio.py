import os
import subprocess
import json

audio_files = [
    r"C:\Users\saipa\Downloads\reel 1.mp3",
    r"C:\Users\saipa\Downloads\reel 2.mp3",
    r"C:\Users\saipa\Downloads\reel 3.mp3"
]

for a in audio_files:
    if os.path.exists(a):
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration,size,bit_rate", "-of", "json", a]
        res = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(res.stdout) if res.stdout else {}
        fmt = info.get("format", {})
        print(f"File: {os.path.basename(a)} | Duration: {fmt.get('duration')}s | Size: {os.path.getsize(a)} bytes")
    else:
        print(f"File: {a} DOES NOT EXIST")

