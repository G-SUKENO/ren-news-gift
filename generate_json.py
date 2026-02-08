import requests
import xml.etree.ElementTree as ET
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1'

def get_real_info(rss_url):
    try:
        # Googleの中継を許可して最終ページへ
        res = requests.get(rss_url, timeout=12, headers={'User-Agent': UA}, allow_redirects=True)
        final_url = res.url
        if "google.com" in final_url: return final_url, ""
        
        soup = BeautifulSoup(res.text, 'html.parser')
        img_url = ""
        # 徹底的に画像タグを探す
        for tag in soup.find_all("meta"):
            prop = tag.get("property", "") or tag.get("name", "")
            if prop in ["og:image", "twitter:image", "thumbnail"]:
                val = tag.get("content", "")
                if val and val.startswith("http") and "google" not in val:
                    img_url = val
                    break
        return final_url, img_url
    except:
        return rss_url, ""

def get_news():
    filename = 'news.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            archive = json.load(f)
    else:
        archive = []

    print(f"--- 既存の {len(archive)} 件を大掃除中 ---")
    
    # ★ 過去の「undefined」や「Google画像」を全スキャンして修正
    # 負荷を考え、今回は「画像がない、またはGoogle画像」のものから先頭30件を強力に修復します
    repair_count = 0
    for item in archive:
        # 1. メディア名が undefined または存在しない場合の修正
        if not item.get('source') or item['source'] == 'undefined':
            item['source'] = 'News'
        
        # 2. 画像がGoogleのもの、または星マークになるURLを修復
        is_bad_img = not item.get('img') or "google" in item.get('img', '') or "placehold.jp" in item.get('img', '')
        if is_bad_img and repair_count < 30:
            print(f"修復中({repair_count+1}/30): {item['title'][:15]}...")
            _, real_img = get_real_info(item['url'])
            if real_img:
                item['img'] = real_img
                print(" -> [成功] 画像を更新しました")
            repair_count += 1
            time.sleep(1)

    # 3. 新着記事の取得（いつもの）
    rss_url = "https://news.google.com/rss/search?q=永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
    try:
        res = requests.get(rss_url, timeout=10)
        root = ET.fromstring(res.content)
        for el in root.findall('.//item')[:10]:
            source_name = el.find('source').text if el.find('source') is not None else "News"
            raw_title = el.find('title').text
            clean_title = re.sub(r' [-|－|:|｜] .*$', '', raw_title).replace(f" - {source_name}", "").strip()
            link = el.find('link').text
            
            if not any(x['title'] == clean_title for x in archive):
                print(f"新着追加: {clean_title[:15]}...")
                f_url, f_img = get_real_info(link)
                pub_date = el.find('pubDate').text
                dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                archive.insert(0, {
                    "title": clean_title, "source": source_name, "url": f_url, "img": f_img,
                    "date": dt.strftime('%Y/%m/%d'), "year": dt.strftime('%Y'), "timestamp": dt.timestamp()
                })
                time.sleep(1)
    except Exception as e:
        print(f"RSS取得エラー: {e}")

    # 保存
    archive.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(archive[:1000], f, ensure_ascii=False, indent=4)
    print("--- 全工程完了 ---")

if __name__ == "__main__":
    get_news()
