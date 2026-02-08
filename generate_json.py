import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
}

def get_image_proxy(img_url):
    if not img_url: return ""
    return f"https://wsrv.nl/?url={urllib.parse.quote(img_url)}&w=400&h=400&fit=cover"

def scrape_modelpress():
    print("モデルプレスを探索中...")
    items = []
    try:
        url = "https://mdpr.jp/tag/15482" # 永瀬廉タグページ
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for art in soup.select('.p-articleList__item')[:8]:
            title = art.select_one('.p-articleList__title').text.strip()
            link = art.select_one('a')['href']
            if not link.startswith('http'): link = "https://mdpr.jp" + link
            img_tag = art.select_one('img')
            img = img_tag.get('src') or img_tag.get('data-src')
            items.append({
                "title": title, "source": "モデルプレス", "url": link, "img": get_image_proxy(img),
                "date": datetime.now().strftime('%Y/%m/%d'), "timestamp": time.time()
            })
    except: pass
    return items

def scrape_natalie():
    print("ナタリーを探索中...")
    items = []
    try:
        url = "https://natalie.mu/search?query=永瀬廉"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for art in soup.select('.NA_card')[:8]:
            title_tag = art.select_one('.NA_card_title')
            if not title_tag: continue
            link = art.select_one('a')['href']
            if not link.startswith('http'): link = "https://natalie.mu" + link
            img = art.select_one('img').get('src')
            items.append({
                "title": title_tag.text.strip(), "source": "ナタリー", "url": link, "img": get_image_proxy(img),
                "date": datetime.now().strftime('%Y/%m/%d'), "timestamp": time.time() - 100 # 並び替え用
            })
    except: pass
    return items

def scrape_oricon():
    print("オリコンを探索中...")
    items = []
    try:
        # オリコンの検索結果（最新順）
        url = "https://www.oricon.co.jp/search/result.php?types=news&word=永瀬廉"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 記事リストのセレクタ
        articles = soup.select('.news-list li')[:8]
        for art in articles:
            title_tag = art.select_one('.title')
            if not title_tag: continue
            link = title_tag.find('a')['href']
            if not link.startswith('http'): link = "https://www.oricon.co.jp" + link
            img_tag = art.select_one('img')
            img = img_tag.get('src') if img_tag else ""
            items.append({
                "title": title_tag.text.strip(), "source": "オリコン", "url": link, "img": get_image_proxy(img),
                "date": datetime.now().strftime('%Y/%m/%d'), "timestamp": time.time() - 200
            })
    except: pass
    return items

def main():
    print("--- 3大サイト直通・永瀬廉NEWS 始動 ---")
    all_news = scrape_modelpress() + scrape_natalie() + scrape_oricon()
    
    # 重複削除（タイトルで判定）
    seen_titles = set()
    unique_news = []
    for news in all_news:
        if news['title'] not in seen_titles:
            seen_titles.add(news['title'])
            unique_news.append(news)
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=4)
    print(f"合計 {len(unique_news)} 件の記事を確保！")

if __name__ == "__main__":
    main()
