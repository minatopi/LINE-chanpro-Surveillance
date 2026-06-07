import os
import json
import requests

URL = "https://minatopi.github.io/chanpro-api/data.json"

ACCESS_TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["LINE_USER_ID"]

CACHE_FILE = "cache.json"


def send_line(msg):
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
        requests.post(url, json=body, headers=headers, timeout=10)
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


def main():
    old = load_cache()

    try:
        new = requests.get(URL, timeout=10).json()
    except Exception as e:
        print("Fetch error:", e)
        return

    changes = []

    for post in new.get("posts", []):
        title = post["title"]
        like = post["like"]
        views = post["views"]

        if title in old:
            o = old[title]

            if o["like"] != like or o["views"] != views:
                changes.append(
                    f"📌 更新\n{title}\n"
                    f"👍 like {o['like']} → {like}\n"
                    f"👀 views {o['views']} → {views}"
                )

        old[title] = {
            "like": like,
            "views": views
        }

    if changes:
        send_line("\n\n".join(changes))

    save_cache(old)


if __name__ == "__main__":
    main()
