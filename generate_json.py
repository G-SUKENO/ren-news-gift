import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
import email.utils
import time
import base64
import re

DATA_FILE = 'news.json'
TARGET_DOMAINS = ["natalie.mu", "oricon.co.jp", "mdpr.jp", "mantan-web.jp", "news.mynavi.jp"]

def decode_google_news_url(url):
    """Googleニュースの特殊なURLから本物のURLを解析する"""
    try:
        path = url.split('/')[-1].split('?')[0]
        # GoogleのURLはbase64でエンコードされている部分があるため、それをデコード
        # ※簡易的な抽出ロジック
        decoded_bytes = base64.b64decode(path + '==', altchars='-_')
        decoded_str = decoded_bytes.decode('latin-1', errors='ignore')
        
        # デコードした文字列からURLらしき部分を抽出
        match = re.search(r'https?://[^\x00-\x1f\x7f-\xff]+', decoded_str)
        if match:
            return match.group(0)
    except:
        pass
    return url

def get_high_res_image(google_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    try:
        # 1. GoogleのURLを解析して本物のURLを推測
        real_url = decode_google_news_url(google_url)
        
        # 2. 本物のURLに直接アクセス（転送を許可）
        r = requests.get(real_url, headers=headers, timeout=10, allow_redirects=True)
        final_url = r.url
        print(f" -> 最終到達先: {final_url[:60]}...")

        if not any(domain in final_url for domain in TARGET_DOMAINS):
            print("    [Skip] 5大サイト対象外")
            return ""

        # 3. 画像抽出
        soup = BeautifulSoup(r.content, "html.parser")
        img = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        
        if img and img.get("content"):
            img_url = img["content"]
            print(f"    [Success] 画像発見: {img_url[:50]}...")
            return img_url
        
        return ""
    except:
        return ""

def fetch_broad_news():
    url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        res = []
        
        # 12件に絞って高精度に解析
        for i in items[:12]:
            title = i.title.text
            print(f"\n解析開始: {title[:25]}...")
            
            p_date = email.utils.parsedate_to_datetime(i.pubDate.text)
            img_url = get_high_res_image(i.link.text)
            
            res.append({
                "title": title,
                "url": i.link.text,
                "date": p_date.strftime('%Y-%m-%d %H:%M'),
                "source": i.source.text if i.source else "News",
                "img": img_url
            })
            time.sleep(1)
            
        return res
    except:
        return []

def update_news_only(new_news):
    if not os.path.exists(DATA_FILE): return
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    full_data["news"] = new_news
    full_data["news"].sort(key=lambda x: x['date'], reverse=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    print("\n--- 全工程完了 ---")

if __name__ == "__main__":
    update_news_only(fetch_broad_news())
