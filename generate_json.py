import requests
import xml.etree.ElementTree as ET
import json
import re
import time
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# より「人間」に見えるようにヘッダーを強化
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

def get_real_url(google_url):
    """Googleの壁（同意画面・リダイレクト警告）を突破して本物のURLを抽出する"""
    try:
        session = requests.Session()
        # 1. Googleの中継ページにアクセス
        res = session.get(google_url, headers=HEADERS, timeout=15, allow_redirects=True)
        
        # もし一発でニュースサイトに飛べたなら、それを返す
        if "google.com" not in res.url:
            return res.url
            
        # 2. 止まってしまった場合、HTMLから本物のリンクを「強奪」する
        html = res.text
        
        # パターンA: <a>タグのhrefから、google以外のリンクを探す
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and 'google.com' not in href:
                return href
        
        # パターンB: JavaScriptのリダイレクト用コードから抽出
        js_url = re.search(r'window\.location\.replace\("(https?://[^"]+)"\)', html)
        if js_url: return js_url.group(1)
        
        # パターンC: 「Redirect Notice」のリンクテキスト自体を探す
        link_text = re.search(r'URL=(https?://[^\s">]+)', html, re.I)
        if link_text: return link_text.group(1)

        return res.url
    except:
        return google_url

def get_image(url):
    """本物のサイトから画像URLを抜き出す"""
    if not url or "google.com" in url: return ""
    try:
        # サイトに潜入
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 優先順位をつけて画像を探す
        img = ""
        og_img = soup.find("meta", property="og:image") or \
                 soup.find("meta", attrs={"name": "twitter:image"}) or \
                 soup.find("link", rel="image_src")
                 
        if og_img:
            img = og_img.get('content') or og_img.get('href')
            
        if img and img.startswith('http'):
            # 魔法の鏡(wsrv.nl)で表示を保証
            return f"https://wsrv.nl/?url={urllib.parse.quote(img)}&w=400&h=400&fit=cover"
    except:
        pass
    return ""

def get_news():
    print("--- 永瀬廉NEWS: GitHubサーバーで壁を粉砕中 ---")
    rss_url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    
    try:
        res = requests.get(rss_url, timeout=15)
        root = ET.fromstring(res.content)
    except:
        print("RSSの取得に失敗しました")
        return

    items = []
    # 成功率を重視して12件
    for el in root.findall('.//item')[:12]:
        source = el.find('source').text if el.find('source') is not None else "ニュース"
        title = el.find('title').text
        clean_title = re.sub(r' - .*$', '', title).strip()
        google_link = el.find('link').text
        
        print(f"解析中: {source}...")
        
        # 1. 物理的にリンク先を特定
        real_url = get_real_url(google_link)
        
        # 2. そのサイトから画像をもぎ取る
        img = get_image(real_url)
        
        if img:
            print(f"  ✨ 画像を確保しました！ ({real_url[:30]}...)")
        else:
            print(f"  ❌ 画像なし (到達先: {real_url[:30]}...)")
            
        pub_date = el.find('pubDate').text
        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
        
        items.append({
            "title": clean_title, "source": source, "url": real_url, "img": img,
            "date": dt.strftime('%Y/%m/%d'), "timestamp": dt.timestamp()
        })
        time.sleep(1)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    print("--- ミッション完了 ---")

if __name__ == "__main__":
    get_news()
