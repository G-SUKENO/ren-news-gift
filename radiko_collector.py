import requests
from bs4 import BeautifulSoup
import time

def collect():
    # 永瀬廉の検索結果ページ（最新順）
    url = "https://news.radiko.jp/search/%E6%B0%B8%E7%80%AC%E5%BB%89/"
    
    # ブラウザであることを証明するための詳細なヘッダー
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'https://news.radiko.jp/',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
    }
    
    try:
        # セッションを使ってCookieを保持しながらアクセス
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"❌ radikoアクセス失敗 (Status: {response.status_code})")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        # radiko newsの検索結果カードのクラス名：list-item
        items = soup.select('.list-item')
        
        for item in items:
            # タイトルとリンク
            title_tag = item.select_one('.list-item__title a')
            # 日付
            date_tag = item.select_one('.list-item__date')
            # 画像
            img_tag = item.select_one('.list-item__img img')
            
            if title_tag and date_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                if link.startswith('/'):
                    link = "https://news.radiko.jp" + link
                
                # 日付整形 (2024.02.15 -> 2024-02-15)
                date_str = date_tag.get_text(strip=True).replace('.', '-')
                thumbnail = img_tag['src'] if img_tag else ""
                
                articles.append({
                    'site_name': 'radiko news',
                    'title': title,
                    'link': link,
                    'date': date_str,
                    'thumbnail': thumbnail
                })
        
        print(f"✅ radiko news 攻略成功：{len(articles)}件取得")
        return articles

    except Exception as e:
        print(f"❌ radikoエラー発生: {e}")
        return []
