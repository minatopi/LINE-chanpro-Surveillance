import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://minatopi.github.io/chanpro-api/data.json"

CACHE_FILE = "cache.json"
HEARTBEAT_FILE = "heartbeat.json"

ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")


# =========================
# LINE送信
# =========================
def send_line(msg: str):
    if not ACCESS_TOKEN or not USER_ID:
        print("LINE env missing, skip")
        return

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


# =========================
# データ取得
# =========================
def fetch():
    r = requests.get(URL, timeout=10)
    return r.json()


# =========================
# キャッシュ
# =========================
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# heartbeat
# =========================
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


# =========================
# メイン処理
# =========================
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

                send_line(
                    "📌 更新検知\n"
                    f"{title}\n"
                    f"👍 {old[title]['like']} → {p['like']}\n"
                    f"👀 {old[title]['views']} → {p['views']}"
                )

        old[title] = p

    print("📊 changes:", changes)

    save_cache(old)
    save_heartbeat()

    print("✅ END")


if __name__ == "__main__":
    main()
