import subprocess
import sys

task_name = "LeaMoreauInstagramScheduler"
python_exe = sys.executable
script_path = r"C:\Users\saipa\Instagram-AI-Automation\LEA_MOREAU\09_CONTENT_PACKS\WEEK_01\scripts\scheduler_daemon.py"

cmd = [
    "schtasks", "/Create", "/F",
    "/TN", task_name,
    "/TR", f'"{python_exe}" "{script_path}" --once',
    "/SC", "MINUTE",
    "/MO", "10"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Create task result:", res.stdout if res.returncode == 0 else res.stderr)
