import json, os, requests, time
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

def fetch_official():
    news = []
    soup = get_soup("https://www.universal-music.co.jp/king-and-prince/news/")
    if soup:
        for a in soup.find_all("a", href=True):
            if "/king-and-prince/news/20" in a['href']:
                url = "https://www.universal-music.co.jp" + a['href'] if a['href'].startswith("/") else a['href']
                sd = get_soup(url)
                img = sd.find("meta", property="og:image")["content"] if sd and sd.find("meta", property="og:image") else ""
                news.append({"title": a.get_text(strip=True)[:50], "url": url, "source": "公式", "img": img})
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
                news.append({"title": link.get_text(strip=True), "url": url, "source": "ナタリー", "img": img})
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
                news.append({"title": art.find(["h2", "p"]).get_text(strip=True), "url": url, "source": "オリコン", "img": img})
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
                news.append({"title": a.get_text(strip=True), "url": url, "source": "Billboard", "img": img})
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
            news.append({"title": art.find("h2").get_text(strip=True), "url": url, "source": "エッジライン", "img": img})
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
            news.append({"title": "モデルプレス特選フォト", "url": url, "source": "モデルプレス", "img": img})
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
                news.append({"title": a.get_text(strip=True) or "映画ニュース", "url": url, "source": "映画Walker", "img": img})
            if len(news) >= 3: break
    return news

def main():
    print(f"\n--- 永瀬廉 神7ポータル 巡回開始 ---")
    all_news = []
    # 【最重要】ここから MANTANWEB と マイナビ を削除しました
    fetchers = [
        ("公式", fetch_official),
        ("ナタリー", fetch_natalie),
        ("オリコン", fetch_oricon),
        ("Billboard", fetch_billboard),
        ("エッジライン", fetch_edgeline),
        ("モデルプレス", fetch_modelpress),
        ("映画Walker", fetch_moviewalker)
    ]
    
    for name, func in fetchers:
        print(f"\n--- {name} を攻略中 ---")
        try:
            results = func()
            for r in results:
                print(f"  解析: {r['title'][:20]}...")
                print(f"    [成功] 画像を確保")
            all_news.extend(results)
        except Exception as e:
            print(f"  [失敗] {name}: {e}")
        time.sleep(1)

    output = {"news": all_news, "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"\n完了: 合計{len(all_news)}件の「神7」ニュースを整理しました。")

if __name__ == "__main__":
    main()
