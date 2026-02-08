import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from datetime import datetime
import time
import re
import os
import glob
import shutil

session = requests.Session()
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}

def sync_images():
    print("--- Image Sync: インスタ画像の同期中 ---")
    source_dir = "ren.nagase.official"
    target_dir = "images"
    os.makedirs(target_dir, exist_ok=True)
    
    # 既存のimagesフォルダ内を一度クリア（整理のため）
    for f in glob.glob(f"{target_dir}/*.jpg"):
        os.remove(f)

    # インスタフォルダから.jpgを探してコピー
    image_list = []
    # instaloaderはサブフォルダを作らない前提、あるいは直下のjpgを全取得
    found_files = glob.glob(f"{source_dir}/*.jpg")
    
    for i, file_path in enumerate(found_files):
        new_name = f"photo_{i+1}.jpg"
        shutil.copy2(file_path, f"{target_dir}/{new_name}")
        image_list.append(f"images/{new_name}")
    
    print(f"  完了: {len(image_list)} 枚の画像を同期しました")
    return image_list

def get_youtube_data():
    print("--- YouTube: スキャン中 ---")
    data = {"featured": None, "regulars": [], "shorts": []}
    try:
        channel_id = "UCSxwcQnzA5K6DvofvBn6ATA"
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        res = session.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'xml')
        entries = soup.find_all('entry')
        for i, entry in enumerate(entries):
            v = {"id": entry.find('yt:videoId').text, "title": entry.find('title').text,
                 "thumbnail": entry.find('media:group').find('media:thumbnail')['url']}
            if i == 0: data["featured"] = v
            elif any(k in v["title"] for k in ["Shorts", "ショート", "#Shorts"]): data["shorts"].append(v)
            else: data["regulars"].append(v)
    except: pass
    return data

def smart_fetch(name, url, keywords):
    items = []
    try:
        res = session.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if any(k in a['href'] for k in keywords):
                title = a.get_text(strip=True)
                if len(title) > 10 and any(k in title for k in ["永瀬廉", "キンプリ"]):
                    items.append({"title": title, "url": urllib.parse.urljoin(url, a['href']), "source": name})
            if len(items) >= 5: break
    except: pass
    return items

def main():
    print("--- 永瀬廉ポータル：フルオート更新 ---")
    
    # 画像同期とリスト作成
    images = sync_images()
    
    # YouTube取得
    yt = get_youtube_data()
    
    # ニュース取得
    news = smart_fetch("公式", "https://www.universal-music.co.jp/king-and-prince/news/", ["/news/"])
    news += smart_fetch("ナタリー", "https://natalie.mu/search?query=永瀬廉", ["/news/"])

    final_data = {
        "images": images,  # ここに画像のパスリストを入れる
        "featured": yt["featured"],
        "regulars": yt["regulars"],
        "shorts": yt["shorts"],
        "news": news
    }

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\n[SUCCESS] news.jsonを更新しました（画像: {len(images)}枚）")

if __name__ == "__main__":
    main()
