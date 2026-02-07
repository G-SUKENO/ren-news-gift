import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

def get_news():
    filename = 'news.json'
    # 1. 既存のデータを読み込む（アーカイブの読み込み）
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                archive = json.load(f)
            except:
                archive = []
    else:
        archive = []

    # URLをキーにして重複チェック
    existing_urls = {item['url'] for item in archive}

    # 2. 新しいニュースを取得
    url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    
    new_items = []
    for item in root.findall('.//item'):
        link = item.find('link').text
        if link not in existing_urls:
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
            
            new_items.append({
                "title": title,
                "url": link,
                "date": date_obj.strftime('%Y/%m/%d'),
                "timestamp": date_obj.timestamp() # ソート用
            })

    # 3. 新旧データを合体して、日付順に並び替える
    combined = new_items + archive
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    # 4. 保存（最大300件くらいまで残す設定）
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:300], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
