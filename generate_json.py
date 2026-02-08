import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# 本物のiPhoneからアクセスしているように見せかける
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1'

def fetch_real_info(rss_url):
    headers = {'User-Agent': UA}
    try:
        # 1. Googleの中継を突破して最終URLへ
        res = requests.get(rss_url, timeout=12, headers=headers, allow_redirects=True)
        final_url = res.url
        
        # Googleのドメインで止まっていたら失敗
        if "google.com" in final_url:
            return final_url, ""

        # 2. ページ解析
        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        
        # 優先順位: OGP -> Twitter -> Itemprop
        tags = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("meta", {"itemprop": "image"}),
            ("link", {"rel": "image_src"})
        ]
        
        for tag, attrs in tags:
            target = soup.find(tag, attrs)
            if target:
                candidate = target.get("content") or target.get("href")
                if candidate and "http" in candidate and "google" not in candidate:
                    img_url = candidate
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

    def normalize_title(t, src):
        # タイトルからメディア名を除去して純粋な見出しにする
        t = re.sub(f' - {src}$', '', t)
        return re.sub(r'[^\w]', '', t)

    existing_urls = {item['url'] for item in archive}
    existing_titles = {normalize_title(item['title'], item['source']) for item in archive[:50] if 'source' in item}
    
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    new_items = []

    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            res = requests.get(rss_url, timeout=10)
            root = ET.fromstring(res.content)
            for item in root.findall('.//item')[:10]:
                raw_title = item.find('title').text
                rss_link = item.find('link').text
                
                # ★メディア名を確実にとる
                source_tag = item.find('source')
                source = source_tag.text if source_tag is not None else "ニュース"
                
                clean_title = re.sub(f' - {source}$', '', raw_title)

                if (normalize_title(clean_title, source) not in existing_titles) and (rss_link not in existing_urls):
                    print(f"取得中: {clean_title[:15]}...")
                    url, img = fetch_real_info(rss_link)
                    
                    pub_date = item.find('pubDate').text
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_items.append({
                        "title": clean_title, "source": source, "url": url, "img": img,
                        "date": date_obj.strftime('%Y/%m/%d'), "year": date_obj.strftime('%Y'),
                        "timestamp": date_obj.timestamp()
                    })
                    existing_titles.add(normalize_title(clean_title, source))
                    existing_urls.add(url)
                    time.sleep(1.5)
        except: continue

    # ★ 既存の「Googleロゴ」や「星マーク」を5件ずつ本物の画像へ書き換える
    for item in archive:
        if not item.get('img') or "google" in item['img'] or "placehold.jp" in item['img']:
            print(f"画像修復中: {item['title'][:10]}...")
            _, real_img = fetch_real_info(item['url'])
            if real_img:
                item['img'] = real_img
                print(" -> 修復成功!")
            time.sleep(1.5)

    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
