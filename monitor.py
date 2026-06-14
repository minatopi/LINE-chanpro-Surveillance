import os
import json
import requests
from datetime import datetime, timezone, timedelta

URL = "https://minatopi.github.io/chanpro-api/data.json"

ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

CACHE_FILE = "output.json"
HEARTBEAT_FILE = "heartbeat.txt"


def send_line(msg):
    url = "https://api.line.me/v2/bot/message/push"

    body = {
        "to": USER_ID,
        "messages": [
            {"type": "text", "text": msg}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    try:
        r = requests.post(url, json=body, headers=headers, timeout=10)
        print("LINE status:", r.status_code)
    except Exception as e:
        print("LINE error:", e)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return []

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("cache load error:", e)
        return []


def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_heartbeat():
    now = datetime.now(timezone.utc).isoformat()

    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        f.write(now)

    print("🫀 heartbeat updated:", now)


def fetch():
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    return r.json()


def cleanup(data):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    result = []
    for item in data:
        try:
            if datetime.fromisoformat(item["updated_at"]) >= cutoff:
                result.append(item)
        except Exception:
            pass

    return result


def main():
    print("🚀 BOT START")

    old = load_cache()
    new = fetch()

    now = datetime.now(timezone.utc).isoformat()
    changes = 0

    old_map = {x["title"]: x for x in old if "title" in x}

    for p in new.get("posts", []):
        title = p.get("title")
        if not title:
            continue

        prev = old_map.get(title)

        if prev:
            if prev.get("like") != p.get("like") or prev.get("views") != p.get("views"):
                changes += 1

                send_line(
                    f"📌 更新検知\n{title}\n"
                    f"👍 {prev.get('like')}→{p.get('like')}\n"
                    f"👀 {prev.get('views')}→{p.get('views')}"
                )

                old.append({
                    "title": title,
                    "like": p.get("like"),
                    "views": p.get("views"),
                    "updated_at": now
                })

        else:
            old.append({
                "title": title,
                "like": p.get("like"),
                "views": p.get("views"),
                "updated_at": now
            })

    old = cleanup(old)

    print("📊 changes:", changes)

    save_cache(old)
    write_heartbeat()

    print("✅ END")


if __name__ == "__main__":
    main()
