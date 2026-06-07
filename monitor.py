import os
import json
import requests

URL = "https://minatopi.github.io/chanpro-api/data.json"

ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

CACHE_FILE = "cache.json"


print("🚀 SCRIPT START")


def send_line(msg):
    print("📩 send_line called")

    url = "https://api.line.me/v2/bot/message/push"

    body = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": msg}]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    try:
        r = requests.post(url, json=body, headers=headers, timeout=10)
        print("📩 LINE status:", r.status_code)
        print("📩 LINE response:", r.text)
    except Exception as e:
        print("❌ LINE ERROR:", e)


def load_cache():
    print("📂 loading cache")

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print("📂 cache loaded:", len(data))
            return data

    print("📂 no cache found")
    return {}


def save_cache(data):
    print("💾 saving cache:", len(data))

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch():
    print("🌐 fetching data...")

    try:
        r = requests.get(URL, timeout=10)
        print("🌐 status:", r.status_code)

        data = r.json()
        print("🌐 posts:", len(data.get("posts", [])))

        return data

    except Exception as e:
        print("❌ FETCH ERROR:", e)
        return None


def main():
    old = load_cache()
    new = fetch()

    if not new:
        print("❌ no data fetched")
        return

    changes = 0

    for p in new["posts"]:
        title = p["title"]
        like = p["like"]
        views = p["views"]

        print(f"🔎 check: {title}")

        if title in old:
            if old[title]["like"] != like or old[title]["views"] != views:
                print("🔥 CHANGE DETECTED")
                changes += 1

                send_line(
                    f"📌 更新検知\n{title}\n"
                    f"👍 {old[title]['like']}→{like}\n"
                    f"👀 {old[title]['views']}→{views}"
                )

        old[title] = {"like": like, "views": views}

    print("📊 total changes:", changes)

    save_cache(old)

    print("✅ SCRIPT END")


if __name__ == "__main__":
    main()
