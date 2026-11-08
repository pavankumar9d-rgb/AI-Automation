#!/usr/bin/env python3
"""
Léa Moreau — Instagram Carousel 01 Publishing Pipeline
Publishes all 3 slides as a single Carousel post to @pavan_create via Meta Graph API.
"""

import sys
import os
import re
import time
import asyncio
import logging
import threading
import socketserver
import http.server
import subprocess
from pathlib import Path
import httpx

logging.getLogger("httpx").setLevel(logging.CRITICAL)

SCRIPT_DIR = Path(__file__).resolve().parent
WEEK_01_DIR = SCRIPT_DIR.parent
STAGING_DIR = WEEK_01_DIR / "STAGING"

SLIDES = [
    "SLIDE_01_MORNING_COFFEE.png",
    "SLIDE_02_OUTFIT_DETAILS.png",
    "SLIDE_03_PARIS_STREET.png"
]

SEO_CAPTION = """A slow autumn morning in Paris ☕🥐 Finding my favorite wicker chair at a corner café in Saint-Germain-des-Prés before the city wakes up. 

There is an effortless art to Parisian lifestyle: ordering a hot café crème, savoring a fresh butter croissant, and watching the morning light bounce off the historic Haussmann limestone facades. 

Today's look is all about French girl aesthetic essentials: an off-the-shoulder cream ribbed knit sweater, delicate layered gold jewelry, and vintage cognac leather — timeless, comfortable, and made for wandering cobblestone streets.

From morning coffee rituals to quiet balcony views overlooking the Paris rooftops, here is your daily reminder to slow down and romanticize the ordinary moments. ☁️✨

Which slide captures your favorite autumn vibe: 1, 2, or 3? Tell me below in the comments! 👇

📌 Save this post for your next Paris trip & autumn outfit inspiration!

—

Fictional AI creator — Léa Moreau ✨

#parisianlifestyle #pariscafes #saintgermain #frenchgirlaesthetic #neutraloutfits #paristravel #slowliving #autumninparis #parisienne #leamoreau"""

MCP_PATH = r"C:\Users\saipa\OneDrive\Desktop\empty\UserssaipaInstagram-AI-Automationinstagram-mcp-william\src"
if MCP_PATH not in sys.path:
    sys.path.insert(0, MCP_PATH)

from instagram_mcp.server import get_fb_client, get_config


class StagingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STAGING_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


def start_tunnel(port: int):
    server = socketserver.TCPServer(("127.0.0.1", port), StagingHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[1/5] Local HTTP server active on port {port} serving {STAGING_DIR}")

    cf_exe = r"C:\Program Files (x86)\cloudflared\cloudflared.exe"
    cf_cmd = [cf_exe, "tunnel", "--url", f"http://127.0.0.1:{port}"]
    cf_proc = subprocess.Popen(cf_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    tunnel_url = None
    registered = False
    start_t = time.time()
    
    while time.time() - start_t < 35:
        line = cf_proc.stderr.readline()
        if not line:
            continue
        if not tunnel_url:
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                tunnel_url = match.group(0)
                print(f"[2/5] Tunnel URL identified: {tunnel_url}")
        if "Registered tunnel connection" in line:
            print("[2/5] Cloudflare connection fully registered and established.")
            registered = True
            break

    if not tunnel_url:
        cf_proc.terminate()
        server.shutdown()
        raise RuntimeError("Failed to establish Cloudflare quick tunnel.")

    # Grace period for global edge DNS propagation
    time.sleep(3)
    return server, cf_proc, tunnel_url


async def publish_carousel_to_instagram():
    PORT = 8748
    server, cf_proc, tunnel_url = start_tunnel(PORT)

    try:
        # Construct public media URLs
        print("[3/5] Staged media URLs prepared for Meta ingestion:")
        media_urls = []
        for s in SLIDES:
            url = f"{tunnel_url}/{s}"
            print(f"  ✓ {s}: {url}")
            media_urls.append(url)

        # Meta Graph API Container Operations
        fb = get_fb_client()
        cfg = get_config()
        ig_user_id = cfg.fb_ig_user_id

        print(f"\n[4/5] Initiating Meta Graph API Carousel Container on @pavan_create ({ig_user_id})...")
        item_container_ids = []

        # 4a. Create individual item containers
        for idx, media_url in enumerate(media_urls, start=1):
            print(f"  -> Creating Carousel Item {idx}/{len(media_urls)} ({SLIDES[idx-1]})...")
            params = {
                "image_url": media_url,
                "is_carousel_item": "true",
            }
            res = await fb.post(f"{ig_user_id}/media", params=params)
            item_id = res.get("id")
            if not item_id:
                raise RuntimeError(f"Meta failed to create item container {idx}: {res}")
            print(f"     ✓ Container ID: {item_id}")
            item_container_ids.append(item_id)

        # 4b. Wait for item containers to be FINISHED
        print("\n  -> Awaiting individual item container processing...")
        for idx, cid in enumerate(item_container_ids, start=1):
            for attempt in range(15):
                status_res = await fb.get(cid, params={"fields": "status_code,status"})
                code = status_res.get("status_code") or status_res.get("status")
                if code == "FINISHED":
                    print(f"     ✓ Item {idx} ready (FINISHED)")
                    break
                await asyncio.sleep(2)

        # 4c. Create parent CAROUSEL container
        print("\n  -> Creating Parent CAROUSEL Container with SEO-optimized caption...")
        parent_params = {
            "media_type": "CAROUSEL",
            "children": ",".join(item_container_ids),
            "caption": SEO_CAPTION
        }
        parent_res = await fb.post(f"{ig_user_id}/media", params=parent_params)
        parent_id = parent_res.get("id")
        if not parent_id:
            raise RuntimeError(f"Meta failed to create parent carousel container: {parent_res}")
        print(f"     ✓ Parent Carousel Container ID: {parent_id}")

        # 4d. Wait for parent container to be FINISHED
        print("  -> Awaiting parent container processing...")
        for attempt in range(15):
            status_res = await fb.get(parent_id, params={"fields": "status_code,status"})
            code = status_res.get("status_code") or status_res.get("status")
            print(f"     Poll {attempt+1}: {code}")
            if code == "FINISHED":
                break
            await asyncio.sleep(2)

        # 5. Final Publishing Call
        print("\n[5/5] Executing me/media_publish to Instagram...")
        pub_res = await fb.post(f"{ig_user_id}/media_publish", params={"creation_id": parent_id})
        media_id = pub_res.get("id")
        if not media_id:
            raise RuntimeError(f"Publish failed: {pub_res}")

        print(f"\n🎉 POST PUBLISHED SUCCESSFULLY! Media ID: {media_id}")
        
        # Fetch live permalink
        details = await fb.get(media_id, params={"fields": "id,permalink,media_type,timestamp,caption"})
        permalink = details.get("permalink")
        print(f"🔗 Live Instagram URL: {permalink}")
        
        return details

    finally:
        print("\nCleaning up Cloudflare tunnel and local HTTP server...")
        cf_proc.terminate()
        server.shutdown()
        print("Cleanup complete.")


if __name__ == "__main__":
    result = asyncio.run(publish_carousel_to_instagram())
    if result:
        print("\n" + "=" * 50)
        print("PUBLISH SUMMARY:")
        print(f"Media ID:   {result.get('id')}")
        print(f"Permalink:  {result.get('permalink')}")
        print(f"Type:       {result.get('media_type')}")
        print(f"Timestamp:  {result.get('timestamp')}")
        print("=" * 50)
