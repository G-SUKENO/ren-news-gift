import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# 人間がブラウザを使っているときと全く同じ情報を送ります
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}

def get_real_info(google_url):
    session = requests.Session()
    try:
        # 1. Googleの中継ページを突破
        res = session.get(google_url, timeout=15, headers=HEADERS, allow_redirects=True)
        final_url = res.url
        
        # 2. 本物のサイト（ナタリー等）を解析
        res = session.get(final_url, timeout=15, headers=HEADERS)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        img_url = ""
        # 優先順位を整理して徹底捜査
        tags = [
            ("meta", {"property": "og:image"}),
            ("meta", {"name": "twitter:image"}),
            ("meta", {"property": "og:image:url"}),
            ("link", {"rel": "image_src"})
        ]
        
        for tag, attrs in tags:
            found = soup.find(tag, attrs)
            if found:
                val = found.get("content") or found.get("href")
                if val and "http" in val and "google" not in val:
                    # ★魔法の鏡(wsrv.nl)を使い、さらに末尾にゴミを付けてブロック回避
                    safe_url = urllib.parse.quote(val)
                    img_url = f"https://wsrv.nl/?url={safe_url}&w=400&h=400&fit=cover&n=-1"
                    break
        return final_url, img_url
    except:
        return google_url, ""

def get_news():
    filename = 'news.json'
    new_archive = []
    # 成功率が高いナタリーとモデルプレスに絞る
    queries = ["永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    
    print("--- 永瀬廉ニュース：成功への挑戦 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            res = requests.get(rss_url, timeout=10)
            root = ET.fromstring(res.content)
            for el in root.findall('.//item')[:5]:
                # メディア名
                source_el = el.find('source')
                s_name = source_el.text if source_el is not None else "ニュース"
                
                raw_title = el.find('title').text
                clean_title = re.sub(r' - .*$', '', raw_title).strip()
                link = el.find('link').text
                
                if not any(x['title'] == clean_title for x in new_archive):
                    print(f"解析中: {clean_title[:10]}... [{s_name}]")
                    _, f_img = get_real_info(link)
                    
                    if f_img:
                        print(f"  -> ✨画像を発見！")
                    else:
                        print(f"  -> ❌画像がまだ見つかりません")
                    
                    pub_date = el.find('pubDate').text
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    new_archive.append({
                        "title": clean_title, "source": s_name, "url": link, "img": f_img,
                        "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
                    })
                    time.sleep(2)
        except: continue

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_archive, f, ensure_ascii=False, indent=4)
    print("--- 完了！ ---")

if __name__ == "__main__":
    get_news()
