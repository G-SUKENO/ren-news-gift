import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_news():
    url = "https://www.universal-music.co.jp/king-and-prince/news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 今回の巡回で見つかった最新ニュースを格納
        scraped_articles = []
        items = soup.select('article, .news-list-item, .news-list li')

        for item in items:
            link_tag = item.find('a', href=True)
            if not link_tag: continue
            
            title_tag = item.select_one('.title, h3, .h3, .text')
            date_tag = item.select_one('.date, time')
            
            href = link_tag['href']
            title = title_tag.get_text(strip=True) if title_tag else ""
            date_str = date_tag.get_text(strip=True) if date_tag else ""

            if title and '/news/' in href:
                full_url = href if href.startswith('http') else "https://www.universal-music.co.jp" + href
                scraped_articles.append({
                    "title": title,
                    "url": full_url,
                    "date": date_str,
                    "image": "images/photo_9.jpg",
                    "site_name": "Official"
                })

        # --- ここから「50件維持」のロジック ---
        data = {"news": [], "shorts": []}
        if os.path.exists('news.json'):
            with open('news.json', 'r', encoding='utf-8') as f:
                try: data = json.load(f)
                except: pass

        # 1. 既存のニュースを取得
        existing_news = data.get('news', [])

        # 2. 新しく取れた記事を、重複を避けて先頭に追加
        new_count = 0
        for article in reversed(scraped_articles): # 古い順にチェックして先頭に差し込む
            if not any(e['url'] == article['url'] for e in existing_news):
                existing_news.insert(0, article)
                new_count += 1

        # 3. 日付でソート（念のため）
        existing_news.sort(key=lambda x: x['date'], reverse=True)

        # 4. 50件を超えたら、古いもの（末尾）を削除
        data['news'] = existing_news[:50]

        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 更新完了: 新着{new_count}件を追加し、合計{len(data['news'])}件を保持しています。")

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    fetch_news()
