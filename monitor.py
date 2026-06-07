import os
import json
import requests

URL = "https://minatopi.github.io/chanpro-api/data.json"

ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

CACHE_FILE = "cache.json"


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
        print("LINE response:", r.text)
    except Exception as e:
        print("LINE error:", e)


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch():
    r = requests.get(URL, timeout=10)
    return r.json()


def main():

    print("🚀 BOT START")

    # ★ここが重要：起動通知（必ず1回だけ）
    send_line("🤖 Bot起動テスト：正常に動作しています")

    old = load_cache()
    new = fetch()

    changes = 0

    for p in new["posts"]:
        title = p["title"]

        if title in old:
            if old[title]["like"] != p["like"] or old[title]["views"] != p["views"]:
                changes += 1

                send_line(
                    f"📌 更新検知\n{title}\n"
                    f"👍 {old[title]['like']}→{p['like']}\n"
                    f"👀 {old[title]['views']}→{p['views']}"
                )

        old[title] = p

    print("📊 changes:", changes)

    save_cache(old)

    print("✅ END")


if __name__ == "__main__":
    main()
