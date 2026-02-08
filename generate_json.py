import requests
import xml.etree.ElementTree as ET
import json
import re
import time
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# 本物のブラウザ（iPhone）のふりをする
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja-jp'
}

def get_real_url(google_url):
    """Googleの『リダイレクト警告ページ』の中から本物のURLを強奪する"""
    try:
        # 1. Googleの中継ページにアクセス
        res = requests.get(google_url, headers=HEADERS, timeout=15, allow_redirects=True)
        html = res.text
        
        # 2. 「Redirect Notice」のページ内にある本物のリンクを探す
        # <a href="本物のURL"> を探す
        real_url = google_url
        soup = BeautifulSoup(html, 'html.parser')
        
        # Googleが「ここをクリックして進んでください」と出すリンクを特定
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and 'google.com' not in href:
                return href
        
        # 3. もし見つからなければ meta refresh を探す
        refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if refresh:
            match = re.search(r'url=(https?://[^\s\'">]+)', refresh.get('content', ''), re.I)
            if match: return match.group(1)
            
        return res.url # 最終的に辿り着いた場所
    except:
        return google_url

def get_image(url):
    """本物のサイトから画像URLを抜き出す"""
    if "google.com" in url: return ""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og:
            val = og.get('content')
            return f"https://wsrv.nl/?url={urllib.parse.quote(val)}&w=400&h=400&fit=cover"
    except: pass
    return ""

def get_news():
    print("--- 永瀬廉NEWS: GitHubサーバーで実行中 ---")
    rss_url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    try:
        root = ET.fromstring(requests.get(rss_url, timeout=15).content)
    except: return

    items = []
    # 成功率を上げるため上位15件
    for el in root.findall('.//item')[:15]:
        source = el.find('source').text if el.find('source') is not None else "ニュース"
        title = el.find('title').text
        clean_title = re.sub(r' - .*$', '', title).strip()
        google_link = el.find('link').text
        
        print(f"解析中: {source}...")
        
        # 1. 壁をこじ開けて本物のURLを取得
        real_url = get_real_url(google_link)
        
        # 2. 画像を取得
        img = get_image(real_url)
        if img: print("  ✨ 画像を確保しました！")
        
        pub_date = el.find('pubDate').text
        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
        items.append({
            "title": clean_title, "source": source, "url": real_url, "img": img,
            "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
        })
        time.sleep(1)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    print("--- 完了 ---")

if __name__ == "__main__":
    get_news()
