import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

def get_news():
    url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    
    news_list = []
    for item in root.findall('.//item')[:15]: # 少し多めに取得
        title = item.find('title').text
        url = item.find('link').text
        pub_date = item.find('pubDate').text
        
        # 日付を読みやすい形式に変換 (例: 2026/02/08)
        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_date = date_obj.strftime('%Y/%m/%d')
        
        news_list.append({
            "title": title,
            "url": url,
            "date": formatted_date
        })
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_news()
