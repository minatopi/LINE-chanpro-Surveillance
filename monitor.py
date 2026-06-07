
import os
import json
import requests
from datetime import datetime

# =========================
# 設定
# =========================

URL = "https://minatopi.github.io/chanpro-api/data.json"

ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

CACHE_FILE = "cache.json"

# =========================
# LINE送信
# =========================

def send_line(msg):

    if not ACCESS_TOKEN or not USER_ID:
        print("❌ LINE_TOKEN or LINE_USER_ID not set")
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

        print("📨 LINE status:", r.status_code)
        print("📨 LINE response:", r.text)

    except Exception as e:
        print("❌ LINE error:", e)

# =========================
# cache読み込み
# =========================

def load_cache():

    if os.path.exists(CACHE_FILE):

        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            print("❌ cache load error:", e)

    return {}

# =========================
# cache保存
# =========================

def save_cache(data):

    try:

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("💾 cache saved")

    except Exception as e:
        print("❌ cache save error:", e)

# =========================
# API取得
# =========================

def fetch():

    headers = {
        "Cache-Control": "no-cache"
    }

    r = requests.get(
        URL,
        headers=headers,
        timeout=10
    )

    r.raise_for_status()

    return r.json()

# =========================
# メイン処理
# =========================

def main():

    print("===================================")
    print("🚀 BOT START")
    print("🕒", datetime.now())
    print("===================================")

    # cache確認
    old = load_cache()

    print("📦 cache exists:", os.path.exists(CACHE_FILE))
    print("📦 cache count:", len(old))

    # API取得
    try:

        new = fetch()

    except Exception as e:

        print("❌ fetch error:", e)

        send_line(f"❌ API取得失敗\n{e}")

        return

    # posts確認
    if "posts" not in new:

        print("❌ posts not found")

        send_line("❌ API形式エラー posts無し")

        return

    # =========================
    # 初回起動
    # =========================

    if not old:

        print("🆕 first launch")

        for p in new["posts"]:

            title = p.get("title", "NO TITLE")

            old[title] = {
                "like": p.get("like", 0),
                "views": p.get("views", 0)
            }

        save_cache(old)

        send_line(
            f"✅ 初回キャッシュ保存完了\n"
            f"件数: {len(old)}"
        )

        return

    # =========================
    # 差分検知
    # =========================

    changes = 0

    for p in new["posts"]:

        title = p.get("title", "NO TITLE")

        current = {
            "like": p.get("like", 0),
            "views": p.get("views", 0)
        }

        # 新規記事
        if title not in old:

            changes += 1

            send_line(
                f"🆕 新規記事\n"
                f"{title}\n"
                f"👍 {current['like']}\n"
                f"👀 {current['views']}"
            )

        else:

            before = old[title]

            # 差分比較
            if before != current:

                changes += 1

                msg = (
                    f"📌 更新検知\n"
                    f"{title}\n\n"
                    f"👍 {before['like']} → {current['like']}\n"
                    f"👀 {before['views']} → {current['views']}"
                )

                print(msg)

                send_line(msg)

        # cache更新
        old[title] = current

    # =========================
    # 保存
    # =========================

    save_cache(old)

    print("===================================")
    print("📊 changes:", changes)
    print("✅ END")
    print("===================================")

# =========================
# 実行
# =========================

if __name__ == "__main__":
    main()
