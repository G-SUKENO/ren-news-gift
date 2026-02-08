import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_real_info(rss_url):
    try:
        res = requests.get(rss_url, timeout=12, headers={'User-Agent': UA}, allow_redirects=True)
        final_url = res.url
        if "google.com" in final_url: return final_url, ""
        
        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        for tag in soup.find_all("meta"):
            prop = tag.get("property", "") or tag.get("name", "")
            if prop in ["og:image", "twitter:image"]:
                val = tag.get("content", "")
                if val and val.startswith("http") and "google" not in val:
                    # ★魔法の鏡(wsrv.nl)を通してブロックを回避
                    img_url = f"https://wsrv.nl/?url={val}&w=200&h=200&fit=cover"
                    break
        return final_url, img_url
    except:
        return rss_url, ""

def get_news():
    filename = 'news.json'
    # 大掃除：一度空にするか、新規で取得し直す
    new_archive = []
    
    # 検索クエリを絞って確実に取得
    queries = ["永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp", "永瀬廉 site:oricon.co.jp"]
    
    print("--- 成功のための1回！ ニュース取得開始 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            res = requests.get(rss_url, timeout=10)
            root = ET.fromstring(res.content)
            for el in root.findall('.//item')[:5]:
                # メディア名の確定的な取得
                source_el = el.find('source')
                source_name = source_el.text if source_el is not None else ""
                
                raw_title = el.find('title').text
                # タイトルの後ろのメディア名を消去
                clean_title = re.sub(r' - .*$', '', raw_title).strip()
                
                # もしsourceが空ならタイトルから推測
                if not source_name or source_name == "News":
                    if "ナタリー" in raw_title: source_name = "ナタリー"
                    elif "モデルプレス" in raw_title: source_name = "モデルプレス"
                    else: source_name = "ニュース"

                link = el.find('link').text
                if not any(x['title'] == clean_title for x in new_archive):
                    print(f"取得中: {clean_title[:15]}... [{source_name}]")
                    f_url, f_img = get_real_info(link)
                    
                    pub_date = el.find('pubDate').text
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_archive.append({
                        "title": clean_title, "source": source_name, "url": f_url, "img": f_img,
                        "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
                    })
                    time.sleep(1.5)
        except Exception as e:
            print(f"エラー: {e}")

    new_archive.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_archive[:100], f, ensure_ascii=False, indent=4)
    print("--- 完了！ ---")

if __name__ == "__main__":
    get_news()
