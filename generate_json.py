import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
}

def get_og_image(url):
    """記事のURLを実際に訪れて、最も高画質な画像を抜き出す"""
    if not url or "google.com" in url: return ""
    try:
        # 1秒待機（マナーと安定のため）
        time.sleep(1)
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # OGP（SNS用の画像指定）を探す
        og = soup.find("meta", property="og:image") or \
             soup.find("meta", attrs={"name": "twitter:image"}) or \
             soup.find("link", rel="image_src")
             
        if og:
            img_url = og.get('content') or og.get('href')
            if img_url:
                # 魔法の鏡(wsrv.nl)で表示を保証
                return f"https://wsrv.nl/?url={urllib.parse.quote(img_url)}&w=400&h=400&fit=cover"
    except:
        pass
    return ""

def scrape_natalie():
    print("ナタリーから記事URLを収穫中...")
    items = []
    try:
        res = requests.get("https://natalie.mu/search?query=永瀬廉", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # ニュース記事（/news/）が含まれるリンクのみを抽出
        for a in soup.find_all('a', href=True):
            if '/news/' in a['href'] and len(items) < 8:
                url = a['href']
                if not url.startswith('http'): url = "https://natalie.mu" + url
                title = a.text.strip()
                if not title: continue
                items.append({"title": title, "url": url, "source": "ナタリー"})
    except: pass
    return items

def scrape_modelpress():
    print("モデルプレスから記事URLを収穫中...")
    items = []
    try:
        res = requests.get("https://mdpr.jp/tag/15482", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.select('.p-articleList__item a')[:8]:
            url = a['href']
            if not url.startswith('http'): url = "https://mdpr.jp" + url
            title = a.select_one('.p-articleList__title')
            if title:
                items.append({"title": title.text.strip(), "url": url, "source": "モデルプレス"})
    except: pass
    return items

def main():
    print("--- 究極の画像取得ミッション 始動 ---")
    
    # 1. まずは記事のURLリストを作る
    raw_list = scrape_natalie() + scrape_modelpress()
    
    # 重複削除
    unique_list = {n['url']: n for n in raw_list}.values()
    
    final_items = []
    for entry in unique_list:
        print(f"画像取得中: {entry['title'][:20]}...")
        # 2. 各記事を訪問して画像を奪取！
        img = get_og_image(entry['url'])
        
        if img:
            print("  ✨ 画像確保！")
        else:
            print("  ⚠️ 画像がありませんでした")
            
        final_items.append({
            "title": entry['title'],
            "source": entry['source'],
            "url": entry['url'],
            "img": img,
            "date": datetime.now().strftime('%Y/%m/%d'),
            "timestamp": time.time()
        })

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_items, f, ensure_ascii=False, indent=4)
    print(f"合計 {len(final_items)} 件を news.json に保存しました。")

if __name__ == "__main__":
    main()
