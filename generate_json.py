import json, requests, time, re
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = 'news.json'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

def get_soup(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        return BeautifulSoup(r.content, "html.parser") if r.status_code == 200 else None
    except: return None

# --- 各サイトの取得ロジック（検証済み神7） ---
def fetch_all_sources():
    results = []
    # 1. 公式 (Universal Music)
    s = get_soup("https://www.universal-music.co.jp/king-and-prince/news/")
    if s:
        for a in s.find_all("a", href=True):
            if "/king-and-prince/news/20" in a['href']:
                u = "https://www.universal-music.co.jp" + a['href'] if a['href'].startswith("/") else a['href']
                sd = get_soup(u)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                results.append({"title": a.get_text(strip=True)[:50], "url": u, "source": "公式", "img": img})
                if len(results) >= 2: break
    
    # 2. ナタリー
    s = get_soup("https://natalie.mu/search/news?query=%E6%B0%B8%E7%80%AC%E5%BB%89")
    if s:
        for art in s.select(".NA_card")[:3]:
            l = art.find("a")
            if l:
                u = "https://natalie.mu" + l['href']
                sd = get_soup(u)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                results.append({"title": l.get_text(strip=True), "url": u, "source": "ナタリー", "img": img})

    # 3. オリコン
    s = get_soup("https://www.oricon.co.jp/prof/637850/article/")
    if s:
        for art in s.select("article")[:3]:
            l = art.find("a")
            if l:
                u = "https://www.oricon.co.jp" + l['href']
                sd = get_soup(u)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                results.append({"title": art.find(["h2", "p"]).get_text(strip=True), "url": u, "source": "オリコン", "img": img})

    # 4. MovieWalker (最新ドメイン)
    s = get_soup("https://press.moviewalker.jp/person/288683/")
    if s:
        for a in s.find_all("a", href=True):
            if "/news/article/" in a['href']:
                u = "https://press.moviewalker.jp" + a['href']
                sd = get_soup(u)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                results.append({"title": a.get_text(strip=True) or "映画ニュース", "url": u, "source": "映画Walker", "img": img})
                break

    return results

def fetch_youtube_id():
    try:
        r = requests.get("https://www.youtube.com/@kp_official0523/videos", headers=HEADERS)
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
        return ids[0] if ids else "dQw4w9WgXcQ"
    except: return "dQw4w9WgXcQ"

def main():
    print("巡回中...")
    news_items = fetch_all_sources()
    yt_id = fetch_youtube_id()
    
    # 1. ニュースから画像URLだけを抽出 (data.images 用)
    all_images = [n['img'] for n in news_items if n['img']]
    
    # 2. HTMLの期待する構造を100%再現
    data = {
        "images": all_images,                     # 画像スライダー用
        "featured": { "id": yt_id },             # メイン動画用 (data.featured.id)
        "regulars": [],                           # 空の配列
        "news": news_items,                       # ニュースリスト
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"完了: {len(news_items)}件のニュースと、YouTube ID({yt_id})を保存しました。")

if __name__ == "__main__":
    main()
