import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_oricon():
    # 永瀬廉のニュース一覧ページ
    url = "https://www.oricon.co.jp/prof/717882/news/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        new_articles = []
        # 記事リストの各項目を取得
        items = soup.select('.news-list article, .news-list-item, li')

        for item in items:
            link_tag = item.find('a', href=True)
            title_tag = item.select_one('.title, h3, .h3')
            date_tag = item.select_one('.date, time')
            img_tag = item.find('img') # ← ここで画像を探す
            
            if link_tag and title_tag:
                title = title_tag.get_text(strip=True)
                # 画像URLの取得（なければデフォルト）
                img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "images/photo_9.jpg"
                
                new_articles.append({
                    "title": title,
                    "url": "https://www.oricon.co.jp" + link_tag['href'] if not link_tag['href'].startswith('http') else link_tag['href'],
                    "date": date_tag.get_text(strip=True) if date_tag else "2026.02.09",
                    "image": img_url, # ← 本物の画像URLを入れる
                    "site_name": "Oricon"
                })

        # 50件蓄積・保存ロジック（中略：以前と同じ50件ローリング）
        # ... (既存の news.json 読み込みと差し込み処理) ...
        
        print(f"✅ オリコン：{len(new_articles)}件の『本物』データを抽出しました。")

    except Exception as e:
        print(f"❌ オリコンエラー: {e}")

if __name__ == "__main__":
    fetch_oricon()
