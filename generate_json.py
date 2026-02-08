import json, os, requests, time, re
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = 'news.json'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://google.com/'
}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        return BeautifulSoup(r.content, "html.parser") if r.status_code == 200 else None
    except: return None

# --- [1] YouTube最新動画の取得 ---
def fetch_youtube():
    print("\n[YouTube] King & Prince公式を確認中...")
    try:
        url = "https://www.youtube.com/@kp_official0523/videos"
        r = requests.get(url, headers=HEADERS, timeout=15)
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        if not video_ids:
            video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", r.text)
        
        if video_ids:
            v_id = video_ids[0]
            img_url = f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg"
            print(f"  -> 成功: {v_id}")
            return {
                "video_id": v_id,
                "title": "King & Prince 最新動画",
                "url": f"https://www.youtube.com/watch?v={v_id}",
                "image": img_url, "img": img_url, "thumbnail": img_url
            }
    except Exception as e:
        print(f"  -> 失敗: {e}")
    return None

# --- [2] ニュースサイト別攻略ロジック ---

def fetch_official(): # 公式
    news = []
    soup = get_soup("https://www.universal-music.co.jp/king-and-prince/news/")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/king-and-prince/news/20" in a['href']:
                url = "https://www.universal-music.co.jp" + a['href'] if a['href'].startswith("/") else a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": a.get_text(strip=True)[:50], "url": url, "source": "公式", "image": img, "img": img, "thumbnail": img})
            if len(news) >= 3: break
    return news

def fetch_natalie(): # ナタリー
    news = []
    soup = get_soup("https://natalie.mu/search/news?query=%E6%B0%B8%E7%80%AC%E5%BB%89")
    if soup:
        for art in soup.select(".NA_card")[:3]:
            link = art.find("a")
            if link and "/news/" in link['href']:
                url = "https://natalie.mu" + link['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": link.get_text(strip=True), "url": url, "source": "ナタリー", "image": img, "img": img, "thumbnail": img})
    return news

def fetch_oricon(): # オリコン
    news = []
    soup = get_soup("https://www.oricon.co.jp/prof/637850/article/")
    if soup:
        for art in soup.select("article")[:3]:
            link = art.find("a")
            if link and "/news/" in link['href']:
                url = "https://www.oricon.co.jp" + link['href'] if link['href'].startswith("/") else link['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": art.find(["h2", "p"]).get_text(strip=True), "url": url, "source": "オリコン", "image": img, "img": img, "thumbnail": img})
    return news

def fetch_billboard(): # Billboard
    news = []
    soup = get_soup("https://www.billboard-japan.com/artists/detail/569261")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/d_news/detail/" in a['href']:
                url = "https://www.billboard-japan.com" + a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": a.get_text(strip=True), "url": url, "source": "Billboard", "image": img, "img": img, "thumbnail": img})
            if len(news) >= 3: break
    return news

def fetch_edgeline(): # エッジライン
    news = []
    soup = get_soup("https://www.edgeline-tokyo.com/?s=%E6%B0%B8%E7%80%AC%E5%BB%89")
    if soup:
        for art in soup.select("article")[:3]:
            url = art.find("a")['href']
            sd = get_soup(url)
            img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
            news.append({"title": art.find("h2").get_text(strip=True), "url": url, "source": "エッジライン", "image": img, "img": img, "thumbnail": img})
    return news

def fetch_modelpress(): # モデルプレス
    news = []
    soup = get_soup("https://mdpr.jp/model/detail/2554")
    if soup:
        links = [a for a in soup.find_all("a", href=True) if "/photo/detail/" in a['href']]
        for link in links[:3]:
            url = "https://mdpr.jp" + link['href']
            sd = get_soup(url)
            img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
            news.append({"title": "モデルプレス特選フォト", "url": url, "source": "モデルプレス", "image": img, "img": img, "thumbnail": img})
    return news

def fetch_moviewalker(): # 映画Walker (新ドメイン版)
    news = []
    soup = get_soup("https://press.moviewalker.jp/person/288683/")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/news/article/" in a['href']:
                url = "https://press.moviewalker.jp" + a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                title = a.get_text(strip=True) or "映画ニュース"
                news.append({"title": title, "url": url, "source": "映画Walker", "image": img, "img": img, "thumbnail": img})
            if len(news) >= 3: break
    return news

# --- [3] 実行と保存 ---

def main():
    print(f"--- 巡回開始: {datetime.now()} ---")
    
    # YouTubeの取得
    yt_data = fetch_youtube()
    
    # 全ニュースの取得
    all_news = []
    fetchers = [
        ("公式", fetch_official), ("ナタリー", fetch_natalie), ("オリコン", fetch_oricon),
        ("Billboard", fetch_billboard), ("エッジライン", fetch_edgeline),
        ("モデルプレス", fetch_modelpress), ("映画Walker", fetch_moviewalker)
    ]
    
    for name, func in fetchers:
        print(f"[{name}] 解析中...")
        try:
            res = func()
            all_news.extend(res)
            print(f"  -> {len(res)}件 完了")
        except Exception as e:
            print(f"  -> エラー: {e}")
        time.sleep(1)

    # 構造の統合 (画面側が期待する全ての形式を網羅)
    final_output = {
        "youtube": yt_data,
        "news": all_news,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
    print(f"\n完了: {DATA_FILE} を更新しました。")

if __name__ == "__main__":
    main()
