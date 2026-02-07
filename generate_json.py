import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

def get_news():
    filename = 'news.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                archive = json.load(f)
                # 古いデータに 'year' がなければ日付から計算して追加する（大掃除）
                for item in archive:
                    if 'year' not in item or item['year'] == "undefined":
                        # "2026/02/08" の最初の4文字を年にする
                        item['year'] = item['date'].split('/')[0]
            except:
                archive = []
    else:
        archive = []

    existing_urls = {item['url'] for item in archive}

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
                "year": date_obj.strftime('%Y'),
                "timestamp": date_obj.timestamp()
            })

    combined = new_items + archive
    # 常に最新順に並び替え
    combined.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined[:1000], f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
