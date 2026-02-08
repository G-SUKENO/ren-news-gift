import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time

# セッションを開始してブラウザに近い挙動にする
session = requests.Session()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.google.com/',
}

def get_og_image(url):
    if not url: return ""
    try:
        time.sleep(0.5)
        res = session.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og:
            return f"https://wsrv.nl/?url={urllib.parse.quote(og.get('content'))}&w=400&h=400&fit=cover"
    except: pass
    return ""

def scrape_modelpress():
    """モデルプレスの検索結果を直接ハッキング"""
    print("--- モデルプレス・特別潜入ミッション ---")
    items = []
    # 検索ページURL（永瀬廉）
    search_url = "https://mdpr.jp/search?query=永瀬廉"
    try:
        res = session.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 記事へのリンクを全スキャン
        for a in soup.select('a[href*="/detail/"]'):
            # タイトルはh2やspanの中に隠れていることが多い
            title = a.get_text(separator=" ", strip=True)
            if len(title) > 10:
                full_url = urllib.parse.urljoin("https://mdpr.jp", a['href'])
                items.append({"title": title, "url": full_url, "source": "モデルプレス"})
            if len(items) >= 5: break
            
        print(f"  成果: {len(items)} 件のモデルプレス記事を発見")
    except: pass
    return items

def smart_fetch(name, url, keywords, domain=""):
    print(f"--- {name} を攻略中 ---")
    items = []
    try:
        res = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for a in links:
            href = a['href']
            if any(k in href for k in keywords):
                title = a.get_text(strip=True)
                if not title and a.find('img'): title = a.find('img').get('alt', '').strip()
                if len(title) > 10:
                    items.append({"title": title, "url": urllib.parse.urljoin(domain or url, href), "source": name})
            if len(items) >= 5: break
        print(f"  成果: {len(items)} 件のリンクを発見")
    except: pass
    return items

def main():
    print("--- 永瀬廉ニュース：5大サイト最終包囲網 ---")
    news_list = []
    
    # モデルプレス専用の特殊ロジックを優先
    news_list += scrape_modelpress()
    
    # 他のサイトは現状の成功ロジックを継続
    news_list += smart_fetch("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"])
    news_list += smart_fetch("オリコン", "https://www.oricon.co.jp/prof/637850/article/", ["/news/"], "https://www.oricon.co.jp")
    news_list += smart_fetch("Billboard", "https://www.billboard-japan.com/artists/detail/569261", ["/d_news/"], "https://www.billboard-japan.com")
    news_list += smart_fetch("RealSound", "https://realsound.jp/?s=永瀬廉", ["/2026/", "/2025/"])

    unique_news = {n['url']: n for n in news_list}.values()
    final_data = []
    for entry in list(unique_news):
        print(f"画像取得: [{entry['source']}] {entry['title'][:15]}...")
        img = get_og_image(entry['url'])
        final_data.append({
            "title": entry['title'], "source": entry['source'], "url": entry['url'], "img": img,
            "date": datetime.now().strftime('%Y/%m/%d'), "timestamp": time.time()
        })

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\n最終報告：合計 {len(final_data)} 件。ついに完全制覇しましたか？")

if __name__ == "__main__":
    main()
