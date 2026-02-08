import json, requests, re, os
from datetime import datetime

DATA_FILE = "news.json"
# G-SUKENOさん指定のチャンネル動画一覧URL
TARGET_URL = "https://www.youtube.com/@kp_official_523/videos"
# 指定の最新動画ID
SPECIFIED_ID = "8HxFsdGL6og"

def fetch_latest_video_id():
    print(f"--- [YouTube] {TARGET_URL} から最新動画をチェック中 ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(TARGET_URL, headers=headers, timeout=15)
        # ページ内から videoId を抽出
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        
        if video_ids:
            # 取得できた中で最も新しいもの
            latest_id = video_ids[0]
            print(f"  成功: 最新動画ID [{latest_id}] を特定しました")
            return latest_id
    except Exception as e:
        print(f"  解析エラー: {e}")
    
    # 万が一解析に失敗した場合は、今回ご指定いただいたIDを返します
    return SPECIFIED_ID

def main():
    # 1. 最新の動画IDを取得（更新があればそれを、なければ指定のIDを使用）
    final_id = fetch_latest_video_id()
    
    # 2. 現在のデータを読み込み（画像やニュースを保護）
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: data = {}
    else:
        data = {}

    # 3. Featured Movieを設定
    data["featured"] = { "id": final_id }
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. 保存
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了: Featured Movieを [{final_id}] に設定しました。")

if __name__ == "__main__":
    main()
