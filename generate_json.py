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
        res = requests.get(rss_url, timeout=12, headers=headers, allow_redirects=True)
        final_url = res.url
        if "news.google.com" in final_url: return final_url, ""

        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        selectors = [("meta", {"property": "og:image"}), ("meta", {"name": "twitter:image"}), ("link", {"rel": "image_src"})]
        
        for tag, attr in selectors:
            target = soup.find(tag, attr)
            if target:
                candidate = target.get("content") or target.get("href")
                if candidate and candidate.startswith("http") and "google" not in candidate:
                    img_url = candidate
                    break
        
        if img_url: print(f"  [Success] 画像発見!")
        else: print(f"  [Failed] 画像なし: {final_url[:30]}")
        return final_url, img_url
    except Exception as e:
        print(f"  [Error] {e}")
        return rss_url, ""

def get_news():
    filename = 'news.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try: archive = json.load(f)
            except: archive = []
    else: archive = []

    print("--- 既存記事の修正(15件) ---")
    updated = 0
    for item in archive:
        if (not item.get('img') or "google" in item.get('img')) and updated < 15:
            print(f"再トライ: {item['title'][:15]}...")
            _, img_url = fetch_article_info(item['url'])
            if img_url:
                item['img'] = img_url
                updated += 1
            time.sleep(1.5)

    def normalize_title(t):
        return re.sub(r'[^\w]', '', re.sub(r' - .*$', '', t))

    existing_urls = {item['url'] for item in archive}
    existing_titles = {normalize_title(item['title']) for item in archive[:50]}
    
    # 検索ワードを広げて網羅性を高める
    queries = ["永瀬廉", "永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp", "永瀬廉 site:oricon.co.jp"]
    new_items = []

    print("\n--- 新着記事の取得 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            root = ET.fromstring(requests.get(rss_url, timeout=10).content)
            for item in root.findall('.//item')[:8]:
                raw_title = item.find('title').text
                rss_link = item.find('link').text
                if (normalize_title(raw_title) not in existing_titles) and (rss_link not in existing_urls):
                    print(f"新着発見: {raw_title[:20]}...")
                    direct_url, img_url = fetch_article_info(rss_link)
                    
                    # ソース（サイト名）の抽出を強化
                    source = "News"
                    title = raw_title
                    for sep in [' - ', ' | ', '：', '｜']:
                        if sep in raw_title:
                            parts = raw_title.rsplit(sep, 1)
                            title, source = parts[0], parts[1]
                            break

                    pub_date = item.find('pubDate').text
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    new_items.append({
                        "title": title, "source": source, "url": direct_url, "img": img_url,
                        "date": date_obj.strftime('%Y/%m/%d'), "year": date_obj.strftime('%Y'),
                        "timestamp": date_obj.timestamp()
                    })
                    existing_titles.add(normalize_title(raw_title))
                    existing_urls.add(direct_url)
                    time.sleep(1.5)
        except: continue

    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
