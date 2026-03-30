import json
import os
from datetime import datetime

LOG_FILE = "logs/interactions.jsonl"

def log_interaction(question, agent, chunks, answer, duration_ms):
    os.makedirs("logs", exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "agent": agent,
        "retrieved_chunks": [{"content": c.page_content[:200],"source":c.metadata.get("filename", "unknown")} for c in chunks],
        "answer": answer,
        "duration_ms": duration_ms
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
        