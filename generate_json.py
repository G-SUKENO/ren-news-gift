import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# 最新のMac用ブラウザを装う
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://news.google.com/'
}

def get_final_data(google_url):
    """Googleの中継を突破して、本当のURLと画像を取得する"""
    try:
        # 1. Googleニュースのリダイレクトを最後まで追いかける
        res = requests.get(google_url, timeout=12, headers=HEADERS, allow_redirects=True)
        final_url = res.url
        
        # 2. 到着したサイトのHTMLを解析
        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        
        # 代表的な画像タグをくまなく探す
        tags = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("link", {"rel": "image_src"}),
            ("meta", {"itemprop": "image"})
        ]
        
        for tag, attrs in tags:
            found = soup.find(tag, attrs)
            if found:
                val = found.get("content") or found.get("href")
                if val and "http" in val and "google" not in val:
                    # 魔法の鏡(wsrv.nl)でブロックを回避
                    img_url = f"https://wsrv.nl/?url={urllib.parse.quote(val)}&w=400&h=400&fit=cover"
                    break
        return final_url, img_url
    except:
        return google_url, ""

def get_news():
    filename = 'news.json'
    # 主要メディアを優先しつつ、全体から取得
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:oricon.co.jp"]
    new_archive = []

    print("--- 永瀬廉ニュース：全メディア画像取得開始 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url, timeout=10).content)
            for el in root.findall('.//item')[:15]:
                source = el.find('source').text if el.find('source') is not None else "News"
                raw_title = el.find('title').text
                # タイトルを綺麗に掃除
                clean_title = re.sub(r' [-|－|:|｜] .*$', '', raw_title).strip()
                clean_title = clean_title.replace(f" - {source}", "").strip()
                
                if not any(x['title'] == clean_title for x in new_archive):
                    print(f"解析中: {clean_title[:12]}... ({source})")
                    real_url, img = get_final_data(el.find('link').text)
                    
                    if img: print("    -> ✨画像確保に成功！")
                    
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
