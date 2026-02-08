import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'

def fetch_article_info(rss_url):
    headers = {'User-Agent': UA}
    try:
        res = requests.get(rss_url, timeout=10, headers=headers, allow_redirects=True)
        final_url = res.url
        if "news.google.com" in final_url: return final_url, ""
        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        for prop in ["og:image", "twitter:image", "thumbnail"]:
            tag = soup.find("meta", {"property": prop}) or soup.find("meta", {"name": prop})
            if tag and tag.get("content"):
                img_url = tag["content"]
                if img_url.startswith("http") and "google" not in img_url: break
        if img_url: print(f"  [Success] Found image")
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

    def normalize_title(t):
        return re.sub(r'[^\w]', '', re.sub(r' - .*$', '', t))

    existing_urls = {item['url'] for item in archive}
    existing_titles = {normalize_title(item['title']) for item in archive[:50]}
    
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    new_items = []

    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url).content)
            for item in root.findall('.//item')[:10]:
                raw_title = item.find('title').text
                rss_link = item.find('link').text
                source_el = item.find('source')
                source = source_el.text if source_el is not None else "News"
                clean_title = re.sub(f' - {source}$', '', raw_title)

                if (normalize_title(clean_title) not in existing_titles) and (rss_link not in existing_urls):
                    print(f"New: {clean_title[:15]}...")
                    url, img = fetch_article_info(rss_link)
                    pub_date = item.find('pubDate').text
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    new_items.append({
                        "title": clean_title, "source": source, "url": url, "img": img,
                        "date": date_obj.strftime('%Y/%m/%d'), "year": date_obj.strftime('%Y'),
                        "timestamp": date_obj.timestamp()
                    })
                    existing_titles.add(normalize_title(clean_title))
                    existing_urls.add(url)
                    time.sleep(1)
        except: continue

    for item in archive[:15]:
        if not item.get('img') or "google" in item.get('img'):
            print(f"Fixing image: {item['title'][:10]}...")
            _, img = fetch_article_info(item['url'])
            if img: item['img'] = img
            time.sleep(1)

    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
