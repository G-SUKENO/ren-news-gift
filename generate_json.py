import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time
import re

session = requests.Session()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.com/',
}

def get_og_image(url):
    if not url: return ""
    try:
        time.sleep(0.3)
        res = session.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og:
            return f"https://wsrv.nl/?url={urllib.parse.quote(og.get('content'))}&w=400&h=400&fit=cover"
    except: pass
    return ""

def scrape_modelpress():
    print("--- モデルプレス：最終突破ルート ---")
    items = []
    url = "https://mdpr.jp/model/detail/2554"
    try:
        res = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for nav in soup.select('.p-breadcrumb, .p-nav, header, footer'):
            nav.decompose()

        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.search(r'/\d+$', href):
                title = a.get_text(strip=True)
                if len(title) < 10:
                    parent = a.find_parent(['article', 'div', 'li'])
                    if parent: title = parent.get_text(" ", strip=True)
                
                title = " ".join(title.split())
                if len(title) > 10 and not any(x in title for x in ["まえだまえだ", "トップページ"]):
                    if any(k in title for k in ["永瀬廉", "キンプリ", "King"]):
                        items.append({"title": title, "url": urllib.parse.urljoin("https://mdpr.jp", href), "source": "モデルプレス"})
            if len(items) >= 5: break
        print(f"  成果: {len(items)} 件を確保")
    except: pass
    return items

def smart_fetch(name, url, keywords, domain=""):
    print(f"--- {name} 攻略中 ---")
    items = []
    try:
        res = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for nav in soup.select('.breadcrumb, nav, header, footer'):
            nav.decompose()
            
        for a in soup.find_all('a', href=True):
            if any(k in a['href'] for k in keywords):
                title = a.get_text(strip=True)
                if not title and a.find('img'): title = a.find('img').get('alt', '').strip()
                if len(title) > 10 and any(k in title for k in ["永瀬廉", "キンプリ", "King"]):
                    items.append({"title": title, "url": urllib.parse.urljoin(domain or url, a['href']), "source": name})
            if len(items) >= 5: break
        print(f"  成果: {len(items)} 件を確保")
    except: pass
    return items

def main():
    print("--- 永瀬廉ニュース：5大サイト完全統合・Billboard修正版 ---")
    news_list = []
    
    # 1. モデルプレス
    news_list += scrape_modelpress()
    
    # 2. 他の4サイト (Billboardのキーワードを修正)
    configs = [
        ("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"]),
        ("オリコン", "https://www.oricon.co.jp/prof/637850/article/", ["/news/"]),
        ("Billboard", "https://www.billboard-japan.com/artists/detail/569261", ["/d_news/"]), # ここを修正
        ("RealSound", "https://realsound.jp/?s=永瀬廉", ["/2026/", "/2025/"])
    ]
    
    for name, url, keywords in configs:
        news_list += smart_fetch(name, url, keywords)

    unique_news = {n['url']: n for n in news_list}.values()
    final_data = []
    
    for entry in list(unique_news):
        print(f"解析中: [{entry['source']}] {entry['title'][:20]}...")
        img = get_og_image(entry['url'])
        final_data.append({
            "title": entry['title'], "source": entry['source'], "url": entry['url'], "img": img,
            "date": datetime.now().strftime('%Y/%m/%d'), "timestamp": time.time()
        })

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：合計 {len(final_data)} 件。今度こそ、全サイトから「本物のニュース」を確保！")

if __name__ == "__main__":
    main()
