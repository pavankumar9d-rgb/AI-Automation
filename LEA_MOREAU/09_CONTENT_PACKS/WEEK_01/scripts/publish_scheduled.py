#!/usr/bin/env python3
"""
Léa Moreau — Autonomous Multi-Format Instagram Publishing Engine (Cross-Platform)
Runs seamlessly on Windows (local) and Ubuntu (GitHub Actions Cloud).
"""

import sys
import os
import re
import json
import time
import asyncio
import logging
import threading
import socketserver
import http.server
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Auto-load .env if running locally
def load_dotenv():
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
        Path(r"C:\Users\saipa\Instagram-AI-Automation\.env"),
        Path(r"c:\Users\saipa\OneDrive\Desktop\empty\.env")
    ]
    for c in candidates:
        if c.exists():
            with open(c, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k not in os.environ:
                            os.environ[k] = v.strip()
            break

load_dotenv()

# Dynamic paths
SCRIPT_DIR = Path(__file__).resolve().parent
WEEK_01_DIR = SCRIPT_DIR.parent
BASE_DIR = WEEK_01_DIR
POSTS_DIR = BASE_DIR / "POSTS"
REELS_DIR = BASE_DIR / "REELS"
LEDGER_PATH = BASE_DIR / "PUBLICATION_LEDGER.json"

IST = timezone(timedelta(hours=5, minutes=30))

PAGE_TOKEN = os.environ.get("INSTAGRAM_FB_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("INSTAGRAM_FB_IG_USER_ID", "17841423433997524")

class StagingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        pass

def get_cloudflared_command(port: int):
    if sys.platform == "win32":
        win_path = r"C:\Program Files (x86)\cloudflared\cloudflared.exe"
        exe = win_path if os.path.exists(win_path) else "cloudflared"
    else:
        exe = "cloudflared"
    return [exe, "tunnel", "--url", f"http://127.0.0.1:{port}"]

def start_tunnel_for_dir(target_dir: Path, port: int = 8752):
    def make_handler(*args, **kwargs):
        return StagingHandler(*args, directory=str(target_dir), **kwargs)

    server = socketserver.TCPServer(("127.0.0.1", port), make_handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    cf_cmd = get_cloudflared_command(port)
    cf_proc = subprocess.Popen(cf_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    tunnel_url = None
    start_t = time.time()
    while time.time() - start_t < 40:
        line = cf_proc.stderr.readline()
        if not line:
            continue
        if not tunnel_url:
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                tunnel_url = match.group(0)
                print(f"Cloudflare Tunnel active: {tunnel_url}")
        if "Registered tunnel connection" in line:
            break

    if not tunnel_url:
        cf_proc.terminate()
        server.shutdown()
        raise RuntimeError("Failed to establish Cloudflare tunnel.")

    time.sleep(3)
    return server, cf_proc, tunnel_url

async def publish_job(job_id: str):
    import httpx
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    target_job = None
    for j in ledger["posts"]:
        if j["id"] == job_id:
            target_job = j
            break

    if not target_job:
        raise ValueError(f"Job {job_id} not found in ledger.")

    job_type = target_job["type"]
    job_dir = BASE_DIR / target_job["directory"]
    
    # Read caption
    caption_path = job_dir / "CAPTION.md"
    caption_text = ""
    if caption_path.exists():
        with open(caption_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"```text\s*(.*?)\s*```", content, re.DOTALL)
            caption_text = match.group(1).strip() if match else content.strip()

    # Load access token
    token = os.environ.get("INSTAGRAM_FB_ACCESS_TOKEN", PAGE_TOKEN)
    ig_user_id = os.environ.get("INSTAGRAM_FB_IG_USER_ID", IG_USER_ID)

    if not token:
        raise ValueError("INSTAGRAM_FB_ACCESS_TOKEN is missing or empty! Cannot publish.")

    print(f"Publishing {job_id} to Instagram account {ig_user_id} using Page Token (len {len(token)})...")

    server, cf_proc, tunnel_url = start_tunnel_for_dir(job_dir, port=8752)
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if job_type == "CAROUSEL":
                slides = target_job["slides"]
                item_container_ids = []
                
                for idx, s in enumerate(slides, start=1):
                    media_url = f"{tunnel_url}/{s}"
                    params = {
                        "image_url": media_url,
                        "is_carousel_item": "true",
                        "access_token": token
                    }
                    res = await client.post(f"https://graph.facebook.com/v23.0/{ig_user_id}/media", params=params)
                    data = res.json()
                    cid = data.get("id")
                    if not cid:
                        raise RuntimeError(f"Failed to create carousel item {idx}: {data}")
                    print(f"Created carousel item {idx}: {cid}")
                    item_container_ids.append(cid)

                # Wait for items to be FINISHED
                for cid in item_container_ids:
                    for _ in range(15):
                        res = await client.get(f"https://graph.facebook.com/v23.0/{cid}", params={"fields": "status_code,status", "access_token": token})
                        st = res.json()
                        if (st.get("status_code") or st.get("status")) == "FINISHED":
                            break
                        await asyncio.sleep(2)

                # Parent carousel
                parent_params = {
                    "media_type": "CAROUSEL",
                    "children": ",".join(item_container_ids),
                    "caption": caption_text,
                    "access_token": token
                }
                res = await client.post(f"https://graph.facebook.com/v23.0/{ig_user_id}/media", params=parent_params)
                parent_data = res.json()
                parent_id = parent_data.get("id")
                if not parent_id:
                    raise RuntimeError(f"Failed to create parent carousel: {parent_data}")
                print(f"Created parent carousel: {parent_id}")

                for _ in range(15):
                    res = await client.get(f"https://graph.facebook.com/v23.0/{parent_id}", params={"fields": "status_code,status", "access_token": token})
                    st = res.json()
                    if (st.get("status_code") or st.get("status")) == "FINISHED":
                        break
                    await asyncio.sleep(2)

                pub_res = await client.post(f"https://graph.facebook.com/v23.0/{ig_user_id}/media_publish", params={"creation_id": parent_id, "access_token": token})
                pub_data = pub_res.json()
                media_id = pub_data.get("id")
                if not media_id:
                    raise RuntimeError(f"Publish failed: {pub_data}")
                
            elif job_type == "REEL":
                video_name = target_job["video"]
                cover_name = target_job.get("cover")
                video_url = f"{tunnel_url}/{video_name}"
                
                reel_params = {
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption_text,
                    "share_to_feed": "true",
                    "access_token": token
                }
                if cover_name and (job_dir / cover_name).exists():
                    reel_params["cover_url"] = f"{tunnel_url}/{cover_name}"

                res = await client.post(f"https://graph.facebook.com/v23.0/{ig_user_id}/media", params=reel_params)
                reel_data = res.json()
                container_id = reel_data.get("id")
                if not container_id:
                    raise RuntimeError(f"Failed to create Reel container: {reel_data}")
                print(f"Created reel container: {container_id}")

                for attempt in range(30):
                    res = await client.get(f"https://graph.facebook.com/v23.0/{container_id}", params={"fields": "status_code,status", "access_token": token})
                    st = res.json()
                    code = st.get("status_code") or st.get("status")
                    if code == "FINISHED":
                        break
                    elif code == "ERROR":
                        raise RuntimeError(f"Reel processing failed on Meta: {st}")
                    await asyncio.sleep(3)

                pub_res = await client.post(f"https://graph.facebook.com/v23.0/{ig_user_id}/media_publish", params={"creation_id": container_id, "access_token": token})
                pub_data = pub_res.json()
                media_id = pub_data.get("id")
                if not media_id:
                    raise RuntimeError(f"Reel publish failed: {pub_data}")

            # Get permalink
            res = await client.get(f"https://graph.facebook.com/v23.0/{media_id}", params={"fields": "id,permalink,timestamp", "access_token": token})
            details = res.json()
            permalink = details.get("permalink", f"https://www.instagram.com/p/{media_id}")
            
            # Update ledger
            target_job["status"] = "PUBLISHED"
            target_job["published_at"] = datetime.now(IST).isoformat()
            target_job["media_id"] = media_id
            target_job["permalink"] = permalink
            ledger["uploaded_count"] = sum(1 for p in ledger["posts"] if p.get("status") == "PUBLISHED")
            with open(LEDGER_PATH, "w", encoding="utf-8") as f:
                json.dump(ledger, f, indent=2)

            print(f"🎉 SUCCESSFULLY PUBLISHED {job_id}: {permalink}")
            return details

        finally:
            cf_proc.terminate()
            server.shutdown()

async def check_and_publish_due_jobs():
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    now_ist = datetime.now(IST)
    print(f"=== Checking due jobs at {now_ist.isoformat()} ===")
    
    for job in ledger.get("posts", []):
        if job.get("status") == "PUBLISHED":
            continue
        sched_dt = datetime.fromisoformat(job["scheduled_time"])
        diff = (now_ist - sched_dt).total_seconds()
        if diff >= 0: # Past due or due now
            print(f"Job {job['id']} is DUE ({job['title']})! Executing publication...")
            await publish_job(job["id"])
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--check":
        asyncio.run(publish_job(sys.argv[1]))
    else:
        asyncio.run(check_and_publish_due_jobs())
