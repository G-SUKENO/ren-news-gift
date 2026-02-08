import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
import base64
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def decode_google_url(google_url):
    """Google Newsの暗号リンクから本物のURLを解読する"""
    try:
        if "articles/" in google_url:
            code = google_url.split("articles/")[1].split("?")[0]
            padding = len(code) % 4
            if padding: code += "=" * (4 - padding)
            decoded_bytes = base64.urlsafe_b64decode(code)
            decoded_str = decoded_bytes.decode('latin-1')
            urls = re.findall(r'https?://[^\s<>"\x00-\x1f]+', decoded_str)
            if urls: return urls[0]
    except: pass
    return google_url

def get_image_from_real_url(real_url):
    """直通URLから画像を抜き出す"""
    try:
        res = requests.get(real_url, timeout=10, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 複数のタグから画像を探す
        selectors = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("link", {"rel": "image_src"})
        ]
        
        for tag, attrs in selectors:
            found = soup.find(tag, attrs)
            if found:
                val = found.get("content") or found.get("href")
                if val and "http" in val and "google" not in val:
                    # 魔法の鏡(wsrv.nl)で表示を確実にする
                    return f"https://wsrv.nl/?url={urllib.parse.quote(val)}&w=400&h=400&fit=cover"
    except: pass
    return ""

def get_news():
    filename = 'news.json'
    # 検索キーワード
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp", "永瀬廉 site:oricon.co.jp"]
    new_archive = []

    print("--- 成功のための最終デコード取得 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url, timeout=10).content)
            for el in root.findall('.//item')[:12]:
                # メディア名
                source = el.find('source').text if el.find('source') is not None else "ニュース"
                raw_title = el.find('title').text
                # タイトルからメディア名を消す
                clean_title = re.sub(r' [-|－|:|｜] .*$', '', raw_title).strip()
                clean_title = clean_title.replace(f" - {source}", "").strip()
                
                if not any(x['title'] == clean_title for x in new_archive):
                    # 1. Googleリンクを解読
                    real_url = decode_google_url(el.find('link').text)
                    print(f"解析中: {clean_title[:10]}... ({source})")
                    
                    # 2. 直通URLから画像取得
                    img = get_image_from_real_url(real_url)
                    if img: print("    -> ✨画像確保に成功！")
                    
                    pub_date = el.find('pubDate').text
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_archive.append({
                        "title": clean_title, "source": source, "url": real_url, "img": img,
                        "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
                    })
                    time.sleep(1)
        except: continue

    new_archive.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_archive[:150], f, ensure_ascii=False, indent=4)
    print("--- 完了！ ---")

if __name__ == "__main__":
    get_news()
