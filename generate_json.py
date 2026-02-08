import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_article_info(rss_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    }
    try:
        res = requests.get(rss_url, timeout=10, headers=headers, allow_redirects=True)
        final_url = res.url
        if "news.google.com" in final_url: return final_url, ""

        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        
        # 優先順位をつけて画像を探す
        selectors = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("meta", {"property": "og:image:secure_url"}),
            ("link", {"rel": "image_src"})
        ]
        
        for tag, attr in selectors:
            target = soup.find(tag, attr)
            if target:
                img_url = target.get("content") or target.get("href")
                if img_url and "http" in img_url and "google" not in img_url:
                    break
        
        return final_url, img_url
    except:
        return rss_url, ""

def get_news():
    filename = 'news.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: archive = json.load(f)
            except: archive = []
    else:
        archive = []

    # 「googleロゴ」や「空」の画像を15件ずつ「本物の画像」に修正していく
    updated_count = 0
    for item in archive:
        is_bad_img = not item.get('img') or "google" in item.get('img') or "placeholder" in item.get('img')
        if is_bad_img and updated_count < 15:
            print(f"画像を再取得中: {item['title'][:15]}...")
            _, img_url = fetch_article_info(item['url'])
            if img_url:
                item['img'] = img_url
                updated_count += 1
            time.sleep(1.2)

    def normalize_title(t):
        t = re.sub(r' - .*$', '', t)
        return re.sub(r'[^\w]', '', t)

    existing_urls = {item['url'] for item in archive}
    existing_titles = {normalize_title(item['title']) for item in archive[:50]}
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp", "永瀬廉 site:oricon.co.jp"]
    new_items = []

    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url, timeout=10).content)
        except: continue
        
        for item in root.findall('.//item')[:8]:
            raw_title = item.find('title').text
            rss_link = item.find('link').text
            norm_title = normalize_title(raw_title)

            if (norm_title not in existing_titles) and (rss_link not in existing_urls):
                direct_url, img_url = fetch_article_info(rss_link)
                if "google" in img_url: img_url = ""
                
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
                time.sleep(1)

    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
