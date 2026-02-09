import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 画像リストの生成 (247枚対応)
def generate_image_list():
    img_dir = 'images'
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    images = [os.path.join(img_dir, f) for f in os.listdir(img_dir) 
              if f.lower().endswith(valid_extensions)]
    
    with open('image_list.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=4)
    print(f"📸 画像リスト完了: {len(images)}枚")

# 2. ニュース取得 (主要サイトをシンプルに巡回)
def fetch_news():
    targets = [
        {"name": "Official", "url": "https://www.universal-music.co.jp/king-and-prince/news/"},
        {"name": "Oricon", "url": "https://www.oricon.co.jp/prof/717882/news/"},
        {"name": "Natalie", "url": "https://natalie.mu/music/tag/1043"}
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    news_data = []

    for target in targets:
        try:
            res = requests.get(target["url"], headers=headers, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 各サイトの共通構造から抽出
            items = soup.select('article, .news-list-item, li')[:10]
            for item in items:
                link = item.find('a', href=True)
                title = item.select_one('h3, .title, .h3')
                if link and title:
                    news_data.append({
                        "title": title.get_text(strip=True),
                        "url": requests.compat.urljoin(target["url"], link['href']),
                        "date": datetime.now().strftime("%Y.%m.%d"),
                        "image": "images/photo_9.jpg", # 後で画像取得強化可能
                        "site_name": target["name"]
                    })
        except: continue

    # 保存 (常に最新50件)
    data = {"news": news_data[:50], "shorts": []}
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"📰 ニュース取得完了: {len(news_data)}件")

if __name__ == "__main__":
    generate_image_list()
    fetch_news()
