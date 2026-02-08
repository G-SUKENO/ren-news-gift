import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

# iPhone17(最新)を装い、Googleの同意画面をパスするクッキーをセット
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Cookie': 'CONSENT=YES+cb.20230531-04-p0.ja+FX+908'
}

def get_real_info(rss_url):
    try:
        # 1. Googleの中継を許可して最終ページへ
        res = requests.get(rss_url, timeout=12, headers=HEADERS, allow_redirects=True)
        final_url = res.url
        
        # もしGoogleで止まっていたら失敗
        if "google.com" in final_url:
            return final_url, ""

        # 2. ページ解析
        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        
        # OGP, Twitter, Thumbnailの順で画像を探す
        for prop in ["og:image", "twitter:image", "thumbnail"]:
            tag = soup.find("meta", {"property": prop}) or soup.find("meta", {"name": prop})
            if tag and tag.get("content"):
                val = tag["content"]
                if val.startswith("http") and "google" not in val:
                    # ★ 魔法の鏡(wsrv.nl)を通してブロックを回避
                    safe_url = urllib.parse.quote(val)
                    img_url = f"https://wsrv.nl/?url={safe_url}&w=300&h=300&fit=cover"
                    break
        return final_url, img_url
    except:
        return rss_url, ""

def get_news():
    filename = 'news.json'
    # ★「成功」のために、一度古いデータをリセットして最新だけを取得
    new_archive = []
    
    # ナタリーとモデルプレスに絞る
    queries = ["永瀬廉 site:natalie.mu", "永瀬廉 site:mdpr.jp"]
    
    print("--- ついに成功させるための挑戦 ---")
    for q in queries:
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            res = requests.get(rss_url, timeout=10, headers=HEADERS)
            root = ET.fromstring(res.content)
            
            for item in root.findall('.//item')[:6]:
                raw_title = item.find('title').text
                source_el = item.find('source')
                source = source_el.text if source_el is not None else "News"
                
                # タイトルから余計なものを消す
                clean_title = re.sub(r' - .*$', '', raw_title).strip()
                rss_link = item.find('link').text
                
                if not any(x['title'] == clean_title for x in new_archive):
                    print(f"解析中: {clean_title[:15]}... [{source}]")
                    _, img = get_real_info(rss_link)
                    
                    if img: print("  -> ✨画像URLの取得に成功！")
                    else: print("  -> ❌まだ画像が見つかりません")
                    
                    pub_date = item.find('pubDate').text
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    new_archive.append({
                        "title": clean_title, "source": source, "url": rss_link, "img": img,
                        "date": date_obj.strftime('%Y/%m/%d'), "year": date_obj.strftime('%Y'),
                        "timestamp": date_obj.timestamp()
                    })
                    time.sleep(2)
        except Exception as e:
            print(f"エラー: {e}")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_archive, f, ensure_ascii=False, indent=4)
    print("--- 完了！ ---")

if __name__ == "__main__":
    get_news()
