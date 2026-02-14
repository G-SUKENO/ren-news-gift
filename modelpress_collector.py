import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def collect():
    print("📡 MODELPRESS：解析中...")
    url = "https://mdpr.jp/model/detail/2554"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # あなたが grep で見つけてくれた「p-articleListItem__title」をターゲットにします
        articles = soup.select('.p-articleListItem__title')
        items = []
        
        for title_tag in articles:
            if len(items) >= 10: break
            
            # 親要素や周辺からリンクと画像を探す
            parent = title_tag.find_parent('a') or title_tag.find_parent('div', class_='p-articleListItem')
            link_tag = parent if parent and parent.name == 'a' else title_tag.find_previous('a') or title_tag.find_next('a')
            
            if not link_tag: continue
            
            title = title_tag.get_text(strip=True)
            link = link_tag.get('href', '')
            if not link.startswith('http'): link = "https://mdpr.jp" + link

            # 画像を探す
            img_tag = None
            if parent:
                img_tag = parent.select_one('img')
            
            thumbnail = ""
            if img_tag:
                thumbnail = img_tag.get('data-src') or img_tag.get('src') or ""
                if thumbnail.startswith('//'): thumbnail = "https:" + thumbnail

            items.append({
                "site_name": "モデルプレス",
                "title": title,
                "link": link,
                "date": datetime.now().strftime("%Y.%m.%d"),
                "thumbnail": thumbnail
            })
            print(f"✅ 発見: {title[:15]}...")
                
        return items
    except Exception as e:
        print(f"❌ 解析失敗: {e}"); return []

if __name__ == '__main__':
    results = collect()
    print(f"\n📊 最終結果: {len(results)} 件")
