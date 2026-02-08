import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime, timedelta
import time
import re
import os
import glob
import shutil

session = requests.Session()
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}

def sync_images():
    print("--- [1] Image Sync ---")
    source_dir = "ren.nagase.official"
    target_dir = "images"
    os.makedirs(target_dir, exist_ok=True)
    image_list = []
    found_files = glob.glob(f"{source_dir}/*.jpg")
    for i, file_path in enumerate(found_files):
        new_name = f"photo_{i+1}.jpg"
        shutil.copy2(file_path, f"{target_dir}/{new_name}")
        image_list.append(f"images/{new_name}")
    return image_list

def get_og_image(url):
    try:
        time.sleep(0.2)
        res = session.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og: return f"https://wsrv.nl/?url={urllib.parse.quote(og.get('content'))}&w=400&h=250&fit=cover"
    except: pass
    return ""

def get_youtube_data():
    print("--- [2] YouTube Scan ---")
    data = {"featured": None, "regulars": []}
    try:
        url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCSxwcQnzA5K6DvofvBn6ATA"
        res = session.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        entries = soup.find_all('entry')
        for i, entry in enumerate(entries):
            v = {"id": entry.find('yt:videoId').text, "title": entry.find('title').text,
                 "thumbnail": entry.find('media:group').find('media:thumbnail')['url']}
            if i == 0: data["featured"] = v
            else: data["regulars"].append(v)
    except: pass
    return data

def smart_fetch(name, url, keywords, limit=8):
    print(f"--- [3] Scraping: {name} ---")
    items = []
    try:
        res = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        current_date = datetime.now().strftime('%Y/%m/%d %H:%M')
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            if any(k in title for k in ["永瀬廉", "キンプリ", "King"]):
                if any(k in a['href'] for k in keywords):
                    full_url = urllib.parse.urljoin(url, a['href'])
                    items.append({"title": title, "url": full_url, "source": name, "date": current_date})
            if len(items) >= limit: break
    except: pass
    return items

def main():
    images = sync_images()
    yt = get_youtube_data()
    news_list = []
    news_list += smart_fetch("公式", "https://www.universal-music.co.jp/king-and-prince/news/", ["/news/"])
    news_list += smart_fetch("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"])
    news_list += smart_fetch("モデルプレス", "https://mdpr.jp/model/detail/2554", ["/detail/"])
    
    unique_news = {n['url']: n for n in news_list}.values()
    final_news = []
    for n in list(unique_news)[:12]: # 最大12件
        print(f"  画像取得中: {n['title'][:15]}...")
        n['img'] = get_og_image(n['url'])
        final_news.append(n)

    final_data = {
        "images": images,
        "featured": yt["featured"],
        "regulars": yt["regulars"],
        "news": final_news
    }
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\n[SUCCESS] 画像{len(images)}枚、ニュース{len(final_news)}件を保存")

if __name__ == "__main__":
    main()
