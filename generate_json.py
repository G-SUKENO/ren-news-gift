import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
import email.utils
import time
import re

DATA_FILE = 'news.json'
# 私たちが攻略した5大ドメイン
TARGET_DOMAINS = ["natalie.mu", "oricon.co.jp", "mdpr.jp", "mantan-web.jp", "news.mynavi.jp"]

def get_real_url_from_google(google_url):
    """Googleの暗号ページを読み込み、中にある本当のリンクを抽出する"""
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    try:
        # Googleの転送ページを直接叩く
        r = requests.get(google_url, headers=headers, timeout=10)
        # HTMLの中から "https://natalie.mu/..." などの本物のURLを探し出す
        soup = BeautifulSoup(r.content, "html.parser")
        a_tag = soup.find("a")
        if a_tag and a_tag.get("href"):
            return a_tag["href"]
        
        # もし見つからなければリダイレクトURLを確認
        if "https://news.google.com" not in r.url:
            return r.url
    except:
        pass
    return google_url

def get_og_image_direct(url):
    """本物のサイトに直接アクセスして、あの時の高画質画像を引っこ抜く"""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # 5大サイト共通のog:imageタグを狙い撃ち
        og_img = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        if og_img and og_img.get("content"):
            return og_img["content"]
    except:
        pass
    return ""

def fetch_broad_news():
    # 永瀬廉のニュースを取得
    rss_url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
    try:
        r = requests.get(rss_url, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        res = []
        
        # 最新の30件を対象にする
        for i in items[:30]:
            title = i.title.text
            google_link = i.link.text
            print(f"解析中: {title[:20]}...")
            
            # 1. Googleの壁を突破して本物のURLを取得
            real_url = get_real_url_from_google(google_link)
            
            # 2. 5大サイトなら直接画像を取りに行く
            img_url = ""
            if any(domain in real_url for domain in TARGET_DOMAINS):
                print(f" -> 5大サイト発見! 直接アクセス中: {real_url[:40]}...")
                img_url = get_og_image_direct(real_url)
                if img_url:
                    print(f"    [成功] 画像を取得しました")
            
            p_date = email.utils.parsedate_to_datetime(i.pubDate.text)
            res.append({
                "title": title,
                "url": google_link,
                "date": p_date.strftime('%Y-%m-%d %H:%M'),
                "source": i.source.text if i.source else "News",
                "img": img_url
            })
            time.sleep(1) # サーバー負荷に配慮
            
        return res
    except Exception as e:
        print(f"エラー: {e}")
        return []

def update_news_only(new_news):
    if not os.path.exists(DATA_FILE): return
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    # 既存の画像（images）やYouTube（featured）を絶対に保護する
    full_data["news"] = new_news
    full_data["news"].sort(key=lambda x: x['date'], reverse=True)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    print(f"\n完了！ 30件のニュースを更新し、5大サイトの画像を復元しました。")

if __name__ == "__main__":
    update_news_only(fetch_broad_news())
