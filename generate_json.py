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

# 本物のブラウザに近いUA
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def decode_google_url(google_url):
    """Google News の URL から本当のリンク先を無理やり抜き出す"""
    try:
        # URLの末尾部分 (articles/以降) を取得
        if "articles/" in google_url:
            code = google_url.split("articles/")[1].split("?")[0]
            # Base64のパディング調整
            padding = len(code) % 4
            if padding:
                code += "=" * (4 - padding)
            
            decoded_bytes = base64.urlsafe_b64decode(code)
            # バイナリデータからURLっぽい文字列を探す
            decoded_str = decoded_bytes.decode('latin-1')
            urls = re.findall(r'https?://[^\s<>"\x00-\x1f]+', decoded_str)
            if urls:
                return urls[0]
    except:
        pass
    return google_url

def get_image_from_real_url(real_url):
    """本当のURLから画像を抜き出す"""
    try:
        res = requests.get(real_url, timeout=10, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # OGP画像を優先
        og_img = soup.find("meta", property="og:image") or \
                 soup.find("meta", attrs={"name": "twitter:image"})
        
        if og_img and og_img.get("content"):
            img_val = og_img["content"]
            # 魔法の鏡(wsrv.nl)を通して表示を確実にする
            safe_url = urllib.parse.quote(img_val)
            return f"https://wsrv.nl/?url={safe_url}&w=400&h=400&fit=cover"
    except:
        pass
    return ""

def get_news():
    filename = 'news.json'
    print("--- URL構造分析＆直通モード ---")
    
    queries = ["永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    new_archive = []

    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            res = requests.get(rss_url, timeout=10)
            root = ET.fromstring(res.content)
            for el in root.findall('.//item')[:6]:
                source_name = el.find('source').text if el.find('source') is not None else "News"
                raw_title = el.find('title').text
                clean_title = re.sub(r' - .*$', '', raw_title).strip()
                google_link = el.find('link').text
                
                if not any(x['title'] == clean_title for x in new_archive):
                    # 1. URLを解読
                    real_url = decode_google_url(google_link)
                    print(f"解析中: {clean_title[:10]}... ({source_name})")
                    print(f"    -> 直通URL: {real_url[:40]}...")
                    
                    # 2. 直通URLから画像を取得
                    img = get_image_from_real_url(real_url)
                    
                    if img:
                        print("    -> ✨画像確保に成功！")
                    else:
                        print("    -> ❌画像なし")

                    pub_date = el.find('pubDate').text
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_archive.append({
                        "title": clean_title, "source": source_name, "url": real_url, "img": img,
                        "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
                    })
                    time.sleep(1)
        except Exception as e:
            print(f"エラー: {e}")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_archive, f, ensure_ascii=False, indent=4)
    print("--- 完了！ ---")

if __name__ == "__main__":
    get_news()
