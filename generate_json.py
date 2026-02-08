import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# デスクトップ版のUAを使う方がGoogleのリダイレクトを回避しやすい
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_real_url_and_img(rss_url):
    try:
        # 1. Googleニュースのリダイレクトを追いかける
        res = requests.get(rss_url, timeout=15, headers={'User-Agent': UA}, allow_redirects=True)
        final_url = res.url
        
        # もしGoogleのドメインのままなら、中身から無理やりURLを探す
        if "google.com" in final_url:
            match = re.search(r'data-url="([^"]+)"', res.text)
            if match:
                final_url = match.group(1)
                res = requests.get(final_url, timeout=10, headers={'User-Agent': UA})

        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        # 画像タグを執念深く探す
        tags = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("link", {"rel": "image_src"})
        ]
        for tag, attr in tags:
            target = soup.find(tag, attr)
            if target:
                val = target.get("content") or target.get("href")
                if val and "http" in val and "google" not in val:
                    img_url = val
                    break
        return final_url, img_url
    except:
        return rss_url, ""

def get_news():
    filename = 'news.json'
    archive = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: archive = json.load(f)
            except: archive = []

    url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        
        # 最新の5件を詳細取得の対象にする
        for item in root.findall('.//item')[:5]:
            raw_title = item.find('title').text
            source_el = item.find('source')
            source = source_el.text if source_el is not None else "News"
            
            # タイトルからソース名を削除 (複数の区切り文字に対応)
            clean_title = re.sub(r' [-|－|:|｜] .*$', '', raw_title).strip()
            clean_title = clean_title.replace(f" - {source}", "").strip()
            
            rss_link = item.find('link').text
            
            if not any(x['title'] == clean_title for x in archive):
                print(f"新着取得中: {clean_title[:15]}...")
                real_url, img_url = get_real_url_and_img(rss_link)
                
                pub_date = item.find('pubDate').text
                date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                
                archive.insert(0, {
                    "title": clean_title,
                    "source": source,
                    "url": real_url,
                    "img": img_url,
                    "date": date_obj.strftime('%Y/%m/%d'),
                    "year": date_obj.strftime('%Y'),
                    "timestamp": date_obj.timestamp()
                })
                time.sleep(2)
        
        # 保存（最新1000件）
        archive.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(archive[:1000], f, ensure_ascii=False, indent=4)
        print("完了！")
            
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    get_news()
