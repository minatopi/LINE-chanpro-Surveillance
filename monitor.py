import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://minatopi.github.io/chanpro-api/data.json"

CACHE_FILE = "cache.json"
HEARTBEAT_FILE = "heartbeat.json"


def fetch():
    r = requests.get(URL, timeout=10)
    return r.json()


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_heartbeat():
    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "last_run": datetime.now(
                    ZoneInfo("Asia/Tokyo")
                ).isoformat()
            },
            f,
            ensure_ascii=False,
            indent=2
        )


def main():
    print("🚀 BOT START")

    old = load_cache()
    new = fetch()

    changes = 0

    for p in new.get("posts", []):
        title = p["title"]

        if title in old:
            if old[title]["like"] != p["like"] or old[title]["views"] != p["views"]:
                changes += 1
                print(f"CHANGE: {title}")

        old[title] = p

    print("📊 changes:", changes)

    save_cache(old)
    save_heartbeat()

    print("✅ END")


if __name__ == "__main__":
    main()
