#!/usr/bin/env python3
"""
Léa Moreau — Autonomous Campaign Scheduler Daemon (Continuous Background Worker)
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(r"C:\Users\saipa\Instagram-AI-Automation\LEA_MOREAU\09_CONTENT_PACKS\WEEK_01")
LOG_DIR = BASE_DIR / "LOGS"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_PATH = BASE_DIR / "PUBLICATION_LEDGER.json"
PUBLISH_SCRIPT = BASE_DIR / "scripts" / "publish_scheduled.py"

logging.basicConfig(
    filename=str(LOG_DIR / "scheduler.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

IST = timezone(timedelta(hours=5, minutes=30))

def sync_with_remote():
    repo_root = BASE_DIR.parent.parent.parent
    try:
        subprocess.run(["git", "pull", "--rebase"], cwd=repo_root, capture_output=True, timeout=15)
    except Exception:
        pass

def push_to_remote():
    repo_root = BASE_DIR.parent.parent.parent
    try:
        subprocess.run(["git", "add", "LEA_MOREAU/09_CONTENT_PACKS/WEEK_01/PUBLICATION_LEDGER.json"], cwd=repo_root, capture_output=True, timeout=15)
        subprocess.run(["git", "commit", "-m", "Auto-sync publication ledger [skip ci]"], cwd=repo_root, capture_output=True, timeout=15)
        subprocess.run(["git", "push", "origin", "main"], cwd=repo_root, capture_output=True, timeout=20)
    except Exception:
        pass

def run_due_jobs():
    sync_with_remote()
    if not LEDGER_PATH.exists():
        return

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    now_ist = datetime.now(IST)
    for job in ledger.get("posts", []):
        if job.get("status") == "PUBLISHED":
            continue

        sched_dt = datetime.fromisoformat(job["scheduled_time"])
        if now_ist >= sched_dt:
            logging.info(f"Triggering scheduled publication for {job['id']} ({job['title']})...")
            cmd = [sys.executable, str(PUBLISH_SCRIPT), job["id"]]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                logging.info(f"Successfully executed {job['id']}: {res.stdout.strip()}")
                push_to_remote()
            else:
                logging.error(f"Failed to publish {job['id']}: {res.stderr.strip()[:300]}")

def daemon_loop():
    logging.info("=== Léa Moreau Campaign Scheduler Daemon Started ===")
    while True:
        try:
            run_due_jobs()
        except Exception as e:
            logging.error(f"Scheduler exception: {e}")
        time.sleep(60)

if __name__ == "__main__":
    if "--once" in sys.argv:
        run_due_jobs()
    else:
        daemon_loop()
