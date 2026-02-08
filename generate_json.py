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

# --- YouTube取得 ---
def fetch_youtube():
    print("\n--- YouTube (King & Prince公式) を攻略中 ---")
    try:
        url = "https://www.youtube.com/@kp_official0523/videos"
        r = requests.get(url, headers=HEADERS, timeout=15)
        video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", r.text)
        if video_ids:
            v_id = video_ids[0]
            print(f"  [成功] 最新動画ID: {v_id}")
            return {
                "video_id": v_id,
                "title": "King & Prince 最新動画",
                "url": f"https://www.youtube.com/watch?v={v_id}",
                "image": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg",
                "thumbnail": f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg"
            }
    except Exception as e:
        print(f"  [失敗] YouTube: {e}")
    return None

# --- ニュース取得関数群 ---
def fetch_official():
    news = []
    soup = get_soup("https://www.universal-music.co.jp/king-and-prince/news/")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/king-and-prince/news/20" in a['href']:
                url = "https://www.universal-music.co.jp" + a['href'] if a['href'].startswith("/") else a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": a.get_text(strip=True)[:50], "url": url, "source": "公式", "img": img, "image": img, "thumbnail": img})
            if len(news) >= 3: break
    return news

def fetch_natalie():
    news = []
    soup = get_soup("https://natalie.mu/search/news?query=%E6%B0%B8%E7%80%AC%E5%BB%89")
    if soup:
        for art in soup.select(".NA_card")[:3]:
            link = art.find("a")
            if link and "/news/" in link['href']:
                url = "https://natalie.mu" + link['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": link.get_text(strip=True), "url": url, "source": "ナタリー", "img": img, "image": img, "thumbnail": img})
    return news

def fetch_oricon():
    news = []
    soup = get_soup("https://www.oricon.co.jp/prof/637850/article/")
    if soup:
        for art in soup.select("article")[:3]:
            link = art.find("a")
            if link and "/news/" in link['href']:
                url = "https://www.oricon.co.jp" + link['href'] if link['href'].startswith("/") else link['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": art.find(["h2", "p"]).get_text(strip=True), "url": url, "source": "オリコン", "img": img, "image": img, "thumbnail": img})
    return news

def fetch_billboard():
    news = []
    soup = get_soup("https://www.billboard-japan.com/artists/detail/569261")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/d_news/detail/" in a['href']:
                url = "https://www.billboard-japan.com" + a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": a.get_text(strip=True), "url": url, "source": "Billboard", "img": img, "image": img, "thumbnail": img})
            if len(news) >= 3: break
    return news

def fetch_edgeline():
    news = []
    soup = get_soup("https://www.edgeline-tokyo.com/?s=%E6%B0%B8%E7%80%AC%E5%BB%89")
    if soup:
        for art in soup.select("article")[:3]:
            url = art.find("a")['href']
            sd = get_soup(url)
            img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
            news.append({"title": art.find("h2").get_text(strip=True), "url": url, "source": "エッジライン", "img": img, "image": img, "thumbnail": img})
    return news

def fetch_modelpress():
    news = []
    soup = get_soup("https://mdpr.jp/model/detail/2554")
    if soup:
        links = [a for a in soup.find_all("a", href=True) if "/photo/detail/" in a['href']]
        for link in links[:3]:
            url = "https://mdpr.jp" + link['href']
            sd = get_soup(url)
            img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
            news.append({"title": "モデルプレス特選フォト", "url": url, "source": "モデルプレス", "img": img, "image": img, "thumbnail": img})
    return news

def fetch_moviewalker():
    news = []
    soup = get_soup("https://press.moviewalker.jp/person/288683/")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/news/article/" in a['href']:
                url = "https://press.moviewalker.jp" + a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": a.get_text(strip=True) or "映画ニュース", "url": url, "source": "映画Walker", "img": img, "image": img, "thumbnail": img})
            if len(news) >= 3: break
    return news

def main():
    print(f"\n--- 復旧・巡回開始 ---")
    all_news = []
    
    # 1. YouTube取得 (HTMLがこれを待っている可能性があります)
    yt_data = fetch_youtube()
    
    # 2. ニュース取得
    fetchers = [
        ("公式", fetch_official), ("ナタリー", fetch_natalie), ("オリコン", fetch_oricon),
        ("Billboard", fetch_billboard), ("エッジライン", fetch_edgeline),
        ("モデルプレス", fetch_modelpress), ("映画Walker", fetch_moviewalker)
    ]
    
    for name, func in fetchers:
        print(f"--- {name} 攻略中 ---")
        try:
            results = func()
            all_news.extend(results)
        except Exception as e:
            print(f"  [失敗] {name}: {e}")
        time.sleep(1)

    # HTMLが期待する構造（youtubeキーとnewsキー）で保存
    output = {
        "youtube": yt_data,
        "news": all_news,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"\n完了: 全{len(all_news)}件 + YouTubeを整理しました。")

if __name__ == "__main__":
    main()
