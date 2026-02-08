import requests
import xml.etree.ElementTree as ET
import json
import os
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

def get_news():
    print("GitHub Actions でニュース取得を開始します...")
    # 永瀬廉さんで検索
    rss_url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        res = requests.get(rss_url, timeout=15)
        root = ET.fromstring(res.content)
    except Exception as e:
        print(f"RSS取得エラー: {e}")
        return

    news_items = []
    # 最新20件を処理
    for item in root.findall('.//item')[:20]:
        source = item.find('source').text if item.find('source') is not None else "News"
        title = item.find('title').text
        clean_title = re.sub(r' - .*$', '', title).strip()
        link = item.find('link').text
        
        # GitHubのIPなら、Googleのリダイレクトを突破できる確率が高い
        img_url = ""
        try:
            r = requests.get(link, headers=headers, timeout=10, allow_redirects=True)
            real_url = r.url
            if "google.com" not in real_url:
                soup = BeautifulSoup(r.text, 'html.parser')
                og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
                if og:
                    img_url = f"https://wsrv.nl/?url={og.get('content')}&w=400&h=400&fit=cover"
        except:
            real_url = link

        pub_date = item.find('pubDate').text
        dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
        news_items.append({
            "title": clean_title, "source": source, "url": real_url, "img": img_url,
            "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
        })
        print(f"取得完了: {clean_title[:15]}")
        time.sleep(1)

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_items, f, ensure_ascii=False, indent=4)
    print("news.json を更新しました。")

if __name__ == "__main__":
    get_news()
