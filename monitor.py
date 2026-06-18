import os
import json
import requests
from datetime import datetime, timezone, timedelta

URL = "https://minatopi.github.io/chanpro-api/data.json"

ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

CACHE_FILE = "cache.json"
OUTPUT_FILE = "output.json"
HEARTBEAT_FILE = "heartbeat.txt"


def send_line(msg):
    if not ACCESS_TOKEN or not USER_ID:
        print("LINE settings not found")
        return

    url = "https://api.line.me/v2/bot/message/push"

    body = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": msg
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    try:
        r = requests.post(
            url,
            json=body,
            headers=headers,
            timeout=10
        )

        print("LINE status:", r.status_code)

    except Exception as e:
        print("LINE error:", e)


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"load error ({path}):", e)
        return default


def save_json(path, data):
    tmp = path + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    os.replace(tmp, path)


def write_heartbeat():
    now = datetime.now(timezone.utc).isoformat()

    with open(
        HEARTBEAT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(now)

    print("🫀 heartbeat updated:", now)


def fetch():
    r = requests.get(URL, timeout=15)
    r.raise_for_status()
    return r.json()


def cleanup_history(history):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    result = []

    for item in history:
        try:
            updated_at = datetime.fromisoformat(
                item["updated_at"]
            )

            if updated_at >= cutoff:
                result.append(item)

        except Exception:
            pass

    return result


def main():
    print("🚀 BOT START")

    now = datetime.now(
        timezone.utc
    ).isoformat()

    cache = load_json(CACHE_FILE, {})
    history = load_json(OUTPUT_FILE, [])

    data = fetch()

    posts = data.get("posts", [])

    print("cache count:", len(cache))
    print("posts count:", len(posts))

    # 初回実行
    if not cache:
        print("📦 first run")

        new_cache = {}

        for p in posts:
            title = p.get("title")

            if not title:
                continue

            new_cache[title] = {
                "like": p.get("like"),
                "views": p.get("views")
            }

        save_json(CACHE_FILE, new_cache)

        history = cleanup_history(history)
        save_json(OUTPUT_FILE, history)

        write_heartbeat()

        print("✅ first run completed")
        return

    changes = 0

    new_cache = {}

    for p in posts:
        title = p.get("title")

        if not title:
            continue

        like = p.get("like")
        views = p.get("views")

        new_cache[title] = {
            "like": like,
            "views": views
        }

        prev = cache.get(title)

        if not prev:
            continue

        if (
            prev.get("like") != like
            or (
                prev.get("views") is not None
                and views is not None
                and (views - prev.get("views")) >= 2
            )
        ):
            changes += 1

            msg = (
                f"📌 更新検知\n"
                f"{title}\n"
                f"👍 {prev.get('like')} → {like}\n"
                f"👀 {prev.get('views')} → {views}"
            )

            send_line(msg)

            history.append({
                "title": title,
                "like_before": prev.get("like"),
                "like_after": like,
                "views_before": prev.get("views"),
                "views_after": views,
                "updated_at": now
            })

    history = cleanup_history(history)

    save_json(CACHE_FILE, new_cache)
    save_json(OUTPUT_FILE, history)

    print("📊 changes:", changes)

    write_heartbeat()

    print("✅ END")


if __name__ == "__main__":
    main()
