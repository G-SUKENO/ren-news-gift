import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# より本物に近いブラウザ設定
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja-JP,ja;q=0.9'
}

def fetch_real_info(rss_url):
    try:
        # Sessionを使ってクッキーを保持し、リダイレクトを追いかける
        session = requests.Session()
        res = session.get(rss_url, timeout=15, headers=HEADERS, allow_redirects=True)
        final_url = res.url
        
        # Googleのページで止まっている場合の対策
        if "google.com" in final_url:
            print(f"  [Wait] Googleの壁に阻まれました: {final_url[:40]}...")
            return final_url, ""

        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        
        # 1. OGPタグを最優先で探す
        og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if og_img and og_img.get("content"):
            img_url = og_img["content"]
        
        # 2. Twitterカードタグを探す
        if not img_url:
            tw_img = soup.find("meta", attrs={"name": "twitter:image"})
            if tw_img: img_url = tw_img.get("content")

        if img_url and img_url.startswith("http") and "google" not in img_url:
            return final_url, img_url
        return final_url, ""
    except Exception as e:
        print(f"  [Error] {e}")
        return rss_url, ""

def get_news():
    # RSSから最新情報を取得
    url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        item = root.findall('.//item')[0] # ★最新の1件だけ取得
        
        raw_title = item.find('title').text
        rss_link = item.find('link').text
        
        # メディア名をGoogleのsourceタグから確実に取得
        source_el = item.find('source')
        source_name = source_el.text if source_el is not None else "ニュース"
        
        # タイトルを綺麗にする
        clean_title = re.sub(f' - {source_name}$', '', raw_title)
        
        print(f"対象記事: {clean_title[:20]} [{source_name}]")
        print("詳細（画像）を取得中...")
        
        final_url, img_url = fetch_real_info(rss_link)
        
        pub_date = item.find('pubDate').text
        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
        
        new_data = {
            "title": clean_title,
            "source": source_name,
            "url": final_url,
            "img": img_url,
            "date": date_obj.strftime('%Y/%m/%d'),
            "year": date_obj.strftime('%Y'),
            "timestamp": date_obj.timestamp()
        }
        
        # 保存
        filename = 'news.json'
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                archive = json.load(f)
        else:
            archive = []
            
        # 重複チェックして先頭に追加
        if not any(x['title'] == clean_title for x in archive):
            archive.insert(0, new_data)
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(archive[:1000], f, ensure_ascii=False, indent=4)
            
        if img_url: print(" [成功] 画像とメディア名を取得しました")
        else: print(" [一部失敗] メディア名は取れましたが、画像が見つかりません")
            
    except Exception as e:
        print(f"RSS取得エラー: {e}")

if __name__ == "__main__":
    get_news()
