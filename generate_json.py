import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_article_info(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find("meta", property="og:image")
        img_url = img_tag["content"] if img_tag else ""
        return response.url, img_url
    except:
        return url, ""

def get_news():
    filename = 'news.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: archive = json.load(f)
            except: archive = []
    else:
        archive = []

    # 画像が空の記事を最大20件まで強制更新（バックフィル）
    updated_count = 0
    for item in archive:
        if (not item.get('img') or item.get('img') == "") and updated_count < 20:
            print(f"画像を取得中: {item['title'][:20]}...")
            _, img_url = fetch_article_info(item['url'])
            item['img'] = img_url
            updated_count += 1
            time.sleep(0.5)

    def normalize_title(t):
        t = re.sub(r' - .*$', '', t)
        return re.sub(r'[^\w]', '', t)

    existing_urls = {item['url'] for item in archive}
    existing_titles = {normalize_title(item['title']) for item in archive[:50]}
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    new_items = []

    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url).content)
        except: continue
        for item in root.findall('.//item')[:10]:
            raw_title = item.find('title').text
            rss_link = item.find('link').text
            norm_title = normalize_title(raw_title)
            if (norm_title not in existing_titles) and (rss_link not in existing_urls):
                direct_url, img_url = fetch_article_info(rss_link)
                parts = raw_title.rsplit(' - ', 1)
                title, source = (parts[0], parts[1]) if len(parts) > 1 else (raw_title, "News")
                pub_date = item.find('pubDate').text
                date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                new_items.append({
                    "title": title, "source": source, "url": direct_url, "img": img_url,
                    "date": date_obj.strftime('%Y/%m/%d'), "year": date_obj.strftime('%Y'),
                    "timestamp": date_obj.timestamp()
                })
                existing_titles.add(norm_title)
                existing_urls.add(direct_url)
                time.sleep(0.5)

    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
