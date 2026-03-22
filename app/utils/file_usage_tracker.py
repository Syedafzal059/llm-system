import csv
import os
import time
from datetime import datetime

USAGE_LOG_FILE = os.getenv("USAGE_LOG_FILE", "usage.csv")


if not os.path.exists(USAGE_LOG_FILE):
    with open(USAGE_LOG_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_id", "prompt", "model_used", "response_length", "tokens", "duration_ms"])

def log_usage(prompt: str, model_used: str, response: str, user_id: str="anonymous"):
    start_time = time.time()
    tokens = len(prompt.split()) + len(response.split()) #simple token estimation
    duration_ms = int((time.time()-start_time)*1000)
    timestamp = datetime.utcnow().isoformat()

    with open(USAGE_LOG_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, user_id, prompt, model_used, len(response), tokens, duration_ms])