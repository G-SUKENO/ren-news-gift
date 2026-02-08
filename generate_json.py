import json, os, requests, re, time
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = 'news.json'
# あなたがGitHubにアップロードしたフォルダ名
IMAGE_DIR = 'images' 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

# --- [1] あなたが魂を込めてアップした画像だけを取得 ---
def get_user_uploaded_images():
    print(f"--- [{IMAGE_DIR}] フォルダをスキャン中 ---")
    images = []
    if os.path.exists(IMAGE_DIR):
        # 拡張子を確認してリスト化（アルファベット順に並び替え）
        files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        for f in files:
            # HTML（index.html）から見た相対パスを作成
            images.append(f"./{IMAGE_DIR}/{f}")
            print(f"  追加: {f}")
    return images

# --- [2] YouTube最新動画 (King & Prince公式) を確実に特定 ---
def fetch_kp_youtube_id():
    print("--- YouTube (King & Prince公式) を解析中 ---")
    try:
        url = "https://www.youtube.com/@kp_official0523/videos"
        r = requests.get(url, headers=HEADERS, timeout=15)
        # YouTubeの最新仕様に基づいたID抽出
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        if ids:
            print(f"  成功: 最新動画ID [{ids[0]}] を確保")
            return ids[0]
    except Exception as e:
        print(f"  エラー: {e}")
    # 万が一の予備も必ずキンプリの公式動画(シンデレラガール)にする
    print("  予備: 公式MVをセットします")
    return "CPXq12c7wHw"

# --- [3] 神7ニュース取得 (検証済みロジック) ---
def fetch_news():
    news_items = []
    print("--- ニュース巡回中 (神7) ---")
    # ナタリー・オリコン・公式などを最小限の負荷で取得
    sources = [
        ("公式", "https://www.universal-music.co.jp/king-and-prince/news/"),
        ("オリコン", "https://www.oricon.co.jp/prof/637850/article/"),
        ("ナタリー", "https://natalie.mu/search/news?query=%E6%B0%B8%E7%80%AC%E5%BB%89")
    ]
    
    for name, url in sources:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.content, "html.parser")
            if "universal" in url:
                links = [a for a in soup.find_all("a", href=True) if "/news/20" in a['href']][:2]
                for l in links:
                    news_items.append({"title": l.get_text(strip=True)[:40], "url": "https://www.universal-music.co.jp"+l['href'], "source": name, "img": ""})
            elif "oricon" in url:
                for art in soup.select("article")[:2]:
                    l = art.find("a")
                    if l: news_items.append({"title": art.find(["h2","p"]).get_text(strip=True)[:40], "url": "https://www.oricon.co.jp"+l['href'], "source": name, "img": ""})
        except: pass
    return news_items

def main():
    # 1. あなたが用意した画像を最優先でロード
    user_images = get_user_uploaded_images()
    
    # 2. キンプリ公式動画IDを特定
    yt_id = fetch_kp_youtube_id()
    
    # 3. ニュースを取得
    news_list = fetch_news()

    # index.html の設計(images, featured.id, news)に完璧に合わせる
    final_data = {
        "images": user_images,            # スライダーはあなたの画像だけ
        "featured": { "id": yt_id },      # 動画はキンプリ公式
        "regulars": [],
        "news": news_list,                # リストは神7
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\n完了: {len(user_images)}枚の画像とYouTube({yt_id})を保存しました。")

if __name__ == "__main__":
    main()
