import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_natalie():
    # 音楽ナタリーのKing & Princeタグページ
    url = "https://natalie.mu/music/tag/1043"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        new_articles = []
        # ナタリーのニュースカード構造に対応
        items = soup.select('.ga-newsList-card')
        
        for item in items:
            link_tag = item.select_one('a')
            title_tag = item.select_one('.c-newsList-card__title')
            date_tag = item.select_one('.c-newsList-card__date')
            
            if link_tag and title_tag:
                title = title_tag.get_text(strip=True)
                # フィルタを「永瀬廉」だけでなく「King & Prince」や「キンプリ」もOKにする
                keywords = ["永瀬廉", "King & Prince", "キンプリ", "King&Prince"]
                if any(k in title for k in keywords):
                    full_url = "https://natalie.mu" + link_tag['href']
                    new_articles.append({
                        "title": title,
                        "url": full_url,
                        "date": date_tag.get_text(strip=True) if date_tag else "New",
                        "image": "images/photo_9.jpg",
                        "site_name": "Natalie"
                    })

        # 50件蓄積ロジック
        data = {"news": [], "shorts": []}
        if os.path.exists('news.json'):
            with open('news.json', 'r', encoding='utf-8') as f:
                try: data = json.load(f)
                except: pass

        existing_news = data.get('news', [])
        new_count = 0
        for article in reversed(new_articles):
            if not any(e['url'] == article['url'] for e in existing_news):
                existing_news.insert(0, article)
                new_count += 1
        
        data['news'] = existing_news[:50]
        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ ナタリー：{new_count}件の新着を追加しました。")

    except Exception as e:
        print(f"❌ ナタリーエラー: {e}")

if __name__ == "__main__":
    fetch_natalie()
