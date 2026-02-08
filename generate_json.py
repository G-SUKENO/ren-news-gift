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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

def decode_google_url(google_url):
    """Google Newsの暗号(CBMi)を解読して本物のURLを抜く"""
    try:
        if "articles/" in google_url:
            code = google_url.split("articles/")[1].split("?")[0]
            # パディングを調整してデコード
            decoded = base64.urlsafe_b64decode(code + '==')
            # バイナリデータから http... の文字列を強引に探す
            match = re.search(rb'https?://[^\s<>"\x00-\x1f\x7f-\xff]+', decoded)
            if match:
                return match.group(0).decode('utf-8')
    except:
        pass
    return google_url

def get_image_from_real_url(real_url):
    """直通URLから画像を抜き出す"""
    try:
        # Googleのドメインのままならスキップ（画像はないため）
        if "google.com" in real_url: return ""
        
        res = requests.get(real_url, timeout=10, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 代表的な画像タグをくまなく捜査
        img_val = ""
        selectors = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("link", {"rel": "image_src"})
        ]
        for tag, attrs in selectors:
            found = soup.find(tag, attrs)
            if found:
                img_val = found.get("content") or found.get("href")
                if img_val and "http" in img_val: break
        
        if img_val:
            # 魔法の鏡(wsrv.nl)でブロックを回避
            return f"https://wsrv.nl/?url={urllib.parse.quote(img_val)}&w=400&h=400&fit=cover"
    except:
        pass
    return ""

def get_news():
    filename = 'news.json'
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    new_archive = []

    print("--- 永瀬廉ニュース：今度こそ「成功」への挑戦 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url, timeout=10).content)
            for el in root.findall('.//item')[:10]:
                source = el.find('source').text if el.find('source') is not None else "ニュース"
                raw_title = el.find('title').text
                clean_title = re.sub(r' [-|－|:|｜] .*$', '', raw_title).strip()
                clean_title = clean_title.replace(f" - {source}", "").strip()
                
                if not any(x['title'] == clean_title for x in new_archive):
                    # 1. 暗号URLを解読
                    real_url = decode_google_url(el.find('link').text)
                    print(f"解析中: {clean_title[:10]}... ({source})")
                    
                    # 2. 直通URLから画像取得
                    img = get_image_from_real_url(real_url)
                    if img:
                        print(f"    -> ✨画像確保に成功！ [URL]: {real_url[:40]}...")
                    
                    pub_date = el.find('pubDate').text
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_archive.append({
                        "title": clean_title, "source": source, "url": real_url, "img": img,
                        "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
                    })
                    time.sleep(0.5)
        except: continue

    new_archive.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_archive[:150], f, ensure_ascii=False, indent=4)
    print("--- 完了！ ---")

if __name__ == "__main__":
    get_news()
