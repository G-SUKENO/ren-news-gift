import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
import email.utils
import time

DATA_FILE = 'news.json'

# 画像抽出を強化する5大ドメイン
TARGET_DOMAINS = ["natalie.mu", "oricon.co.jp", "mdpr.jp", "mantan-web.jp", "news.mynavi.jp"]

def get_high_res_image(url):
    """各サイトのURLからog:imageを抽出する"""
    try:
        # 5大サイト以外は負荷軽減のためスキップ
        if not any(domain in url for domain in TARGET_DOMAINS):
            return ""
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # og:image メタタグを探す
        og_img = soup.find("meta", property="og:image")
        if og_img:
            return og_img["content"]
        return ""
    except:
        return ""

def fetch_broad_news():
    url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        res = []
        
        # 最新15件程度に対して、詳細な画像抽出を行う（全件やると時間がかかるため）
        for i in items[:15]:
            p_date = email.utils.parsedate_to_datetime(i.pubDate.text)
            link = i.link.text
            
            print(f"解析中: {i.title.text[:20]}...")
            img_url = get_high_res_image(link)
            
            res.append({
                "title": i.title.text,
                "url": link,
                "date": p_date.strftime('%Y-%m-%d %H:%M'),
                "source": i.source.text if i.source else "News",
                "img": img_url
            })
            time.sleep(0.5) # サーバーに優しく
            
        return res
    except:
        return []

def update_news_only(new_news):
    if not os.path.exists(DATA_FILE):
        print("エラー: news.jsonが見つかりません。")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    # ニュースだけを更新（画像・YouTube設定は保持）
    full_data["news"] = new_news
    full_data["news"].sort(key=lambda x: x['date'], reverse=True)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    print(f"完了: 5大サイトから画像を抽出しました。")

if __name__ == "__main__":
    update_news_only(fetch_broad_news())
