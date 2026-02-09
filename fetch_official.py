import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_news():
    url = "https://www.universal-music.co.jp/king-and-prince/news/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        new_articles = []
        # ユニバーサルのサイト構造に合わせて抽出（クラス名は現状に合わせる）
        for item in soup.select('.news-list li, .newsList li'):
            title_tag = item.select_one('.title')
            date_tag = item.select_one('.date')
            link_tag = item.select_one('a')
            img_tag = item.select_one('img')
            
            if title_tag and link_tag:
                new_articles.append({
                    "title": title_tag.get_text(strip=True),
                    "url": link_tag['href'] if link_tag['href'].startswith('http') else "https://www.universal-music.co.jp" + link_tag['href'],
                    "date": date_tag.get_text(strip=True) if date_tag else "",
                    "image": img_tag['src'] if img_tag else "images/photo_9.jpg",
                    "site_name": "Official"
                })

        # 既存のデータを読み込む（Shortsを消さないため）
        data = {"news": [], "shorts": []}
        if os.path.exists('news.json'):
            with open('news.json', 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except:
                    pass

        # ニュースだけを最新の50件に差し替え（Shortsは維持）
        data['news'] = new_articles[:50]

        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ ニュースを{len(data['news'])}件更新しました。")

    except Exception as e:
        print(f"❌ エラー発生: {e}")

if __name__ == "__main__":
    fetch_news()
