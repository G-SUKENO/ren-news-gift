import json, requests, re, os
from datetime import datetime

DATA_FILE = "news.json"
# 公式のショート動画ページ
SHORTS_URL = "https://www.youtube.com/@kp_official_523/shorts"

def fetch_shorts():
    print(f"--- [YouTube Shorts] SHORTスライド用の動画を収集中 ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(SHORTS_URL, headers=headers, timeout=15)
        short_ids = list(dict.fromkeys(re.findall(r'/shorts/([a-zA-Z0-9_-]{11})', r.text)))
        
        shorts_data = []
        for vid in short_ids[:15]:
            shorts_data.append({
                "id": vid,
                "title": "King & Prince Short",
                "url": f"https://www.youtube.com/shorts/{vid}",
                "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
            })
        print(f"  成功: {len(shorts_data)} 件のショート動画を取得")
        return shorts_data
    except Exception as e:
        print(f"  エラー: {e}")
        return []

def main():
    # 1. ショート動画データを取得
    shorts_list = fetch_shorts()
    
    # 2. 現在のデータを読み込み
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: data = {}
    else:
        data = {}

    # 3. データの整理
    # 'shorts'という新しい枠を作り、さらにJSがNew Arrivals枠(news)を
    # 探している場合に備えて、newsの中身もショート動画に差し替えます。
    data["shorts"] = shorts_list
    data["news"] = shorts_list  # New Arrivalsの表示箇所をショート動画にするため
    
    # 見出しを「SHORT」に変更するためのフラグ（JS側で使用）
    data["section_title"] = "SHORT"
    
    # 既存の画像とFeatured Movieを保護
    if "featured" not in data or not data["featured"].get("id"):
        data["featured"] = {"id": "8HxFsdGL6og"}
    
    data["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了: New Arrivalsを『SHORT』スライドとして再構成しました。")

if __name__ == "__main__":
    main()
