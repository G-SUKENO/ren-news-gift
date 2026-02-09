import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def collect():
    print("📡 STARTO ENTERTAINMENTを単独攻略中...")
    url = "https://starto.jp/s/p/artist/41/news"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    items = []
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # HTML内に転がっている「detail/数字」をすべて拾う
        ids = re.findall(r'detail/(\d+)', res.text)
        unique_ids = sorted(list(set(ids)), reverse=True)

        for news_id in unique_ids[:5]:
            detail_url = f"https://starto.jp/s/p/news/detail/{news_id}?artist=41"
            res_d = requests.get(detail_url, headers=headers, timeout=5)
            soup = BeautifulSoup(res_d.text, 'html.parser')
            
            title = soup.find('meta', property='og:title')
            title = re.sub(r'：STARTO.*$', '', title['content']).strip() if title else "STARTO News"
            img = soup.find('meta', property='og:image')
            
            items.append({
                "site_name": "STARTO ENTERTAINMENT",
                "title": title,
                "link": detail_url,
                "date": datetime.now().strftime("%Y.%m.%d"),
                "thumbnail": img['content'] if img else ""
            })
            print(f"✅ STARTO: {title[:15]}...")
    except Exception as e:
        print(f"❌ STARTOでエラー: {e}")
    return items
