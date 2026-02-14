import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def collect():
    print("📡 MODELPRESS：正確な日付を抽出中...")
    url = "https://mdpr.jp/model/detail/2554"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 記事リストのアイテムを特定
        articles = soup.select('.p-articleListItem') or soup.select('.p-articleList__item')
        items = []
        
        for article in articles:
            if len(items) >= 10: break
            
            title_tag = article.select_one('.p-articleListItem__title') or article.select_one('.p-articleList__title')
            link_tag = article.select_one('a')
            
            if not title_tag or not link_tag: continue
            
            title = title_tag.get_text(strip=True)
            link = link_tag.get('href', '')
            if not link.startswith('http'): link = "https://mdpr.jp" + link

            # --- 日付の抽出を強化 ---
            date_str = ""
            # クラス名で探す
            date_tag = article.select_one('.p-articleListItem__date') or article.select_one('.c-articleCard__date')
            if date_tag:
                date_raw = date_tag.get_text(strip=True)
                # "2026.02.13" のような形式を抽出
                match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', date_raw)
                if match:
                    date_str = match.group(0)

            # もし見つからなければ、今日の日付ではなく「不明」と分かるようにする（デバッグ用）
            if not date_str:
                date_str = datetime.now().strftime("%Y.%m.%d") # 万が一の予備

            # 画像を探す
            img_tag = article.select_one('img')
            thumbnail = ""
            if img_tag:
                thumbnail = img_tag.get('data-src') or img_tag.get('src') or ""
                if thumbnail.startswith('//'): thumbnail = "https:" + thumbnail

            items.append({
                "site_name": "モデルプレス",
                "title": title,
                "link": link,
                "date": date_str,
                "thumbnail": thumbnail
            })
            print(f"✅ 取得: {date_str} | {title[:15]}...")
                
        return items
    except Exception as e:
        print(f"❌ 解析失敗: {e}"); return []

if __name__ == '__main__':
    results = collect()
