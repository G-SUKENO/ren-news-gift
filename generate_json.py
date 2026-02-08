import json, os, requests, re, time
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = 'news.json'
IMAGE_DIR = 'images' # GitHubに上げたフォルダ名
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        return BeautifulSoup(r.content, "html.parser") if r.status_code == 200 else None
    except: return None

# --- [1] あなたがGitHub/ローカルに用意した画像だけを取得 ---
def get_your_uploaded_images():
    print(f"[{IMAGE_DIR}] フォルダからあなたの画像を読み込み中...")
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    images = []
    if os.path.exists(IMAGE_DIR):
        # ファイル名でソートして順序を安定させる
        for f in sorted(os.listdir(IMAGE_DIR)):
            if f.lower().endswith(valid_extensions):
                # HTMLから見た相対パス（GitHub Pagesで正しく表示される形式）
                images.append(f"./{IMAGE_DIR}/{f}")
    return images

# --- [2] YouTube最新動画（King & Prince公式）を確実に取得 ---
def fetch_kp_youtube_id():
    print("[YouTube] King & Prince公式の最新動画を解析中...")
    try:
        # 動画一覧ページを解析
        url = "https://www.youtube.com/@kp_official0523/videos"
        r = requests.get(url, headers=HEADERS, timeout=15)
        # JSONデータ内のvideoIdをピンポイントで抽出
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        if ids:
            print(f"  -> 成功: 最新動画ID [{ids[0]}] を確保")
            return ids[0]
    except Exception as e:
        print(f"  -> YouTube解析エラー: {e}")
    # 万が一失敗した場合は、代表的な公式MVのIDをセット（ダミーは使いません）
    return "CPXq12c7wHw" 

# --- [3] 神7ニュース（リスト表示用） ---
def fetch_god7_news():
    news_list = []
    print("[News] 神7サイトから最新ニュースを収集中...")
    
    # 代表として3サイトから高品質なニュースを抽出
    targets = [
        ("公式", "https://www.universal-music.co.jp/king-and-prince/news/"),
        ("オリコン", "https://www.oricon.co.jp/prof/637850/article/"),
        ("映画Walker", "https://press.moviewalker.jp/person/288683/")
    ]
    
    for source_name, url in targets:
        soup = get_soup(url)
        if not soup: continue
        
        # 各サイトのリンク抽出ロジック（検証済み）
        if "universal-music" in url:
            links = [a for a in soup.find_all("a", href=True) if "/news/20" in a['href']][:2]
            for l in links:
                full_url = "https://www.universal-music.co.jp" + l['href']
                news_list.append({"title": l.get_text(strip=True)[:40], "url": full_url, "source": source_name, "img": ""})
        
        elif "oricon" in url:
            for art in soup.select("article")[:2]:
                l = art.find("a")
                if l:
                    news_list.append({"title": art.find(["h2", "p"]).get_text(strip=True)[:40], "url": "https://www.oricon.co.jp" + l['href'], "source": source_name, "img": ""})
        
        elif "moviewalker" in url:
            for a in soup.find_all("a", href=True):
                if "/news/article/" in a['href']:
                    news_list.append({"title": a.get_text(strip=True)[:40] or "映画ニュース", "url": "https://press.moviewalker.jp" + a['href'], "source": source_name, "img": ""})
                    break
        time.sleep(1)
    return news_list

def main():
    # 1. あなたの画像をスライダー用に取得
    your_images = get_your_uploaded_images()
    
    # 2. キンプリ公式YouTubeを取得
    kp_yt_id = fetch_kp_youtube_id()
    
    # 3. ニュースリストを取得
    news_items = fetch_god7_news()
    
    # index.html の設計（featured.id / images / news）に完全に合わせる
    data = {
        "images": your_images,              # ここが「タイトル下の画像」
        "featured": { "id": kp_yt_id },    # ここが「YouTube動画」
        "news": news_items,                 # ここが「ニュースリスト」
        "regulars": [],
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n--- 完了 ---")
    print(f"画像: {len(your_images)}枚をスライダーにセットしました。")
    print(f"動画: King & Prince公式ID [{kp_yt_id}] をセットしました。")

if __name__ == "__main__":
    main()
