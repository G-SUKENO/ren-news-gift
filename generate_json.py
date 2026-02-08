import json, os, requests, time, re
from bs4 import BeautifulSoup
from datetime import datetime
import email.utils

DATA_FILE = 'news.json'

def get_real_url(google_url):
    """Googleの転送を突破して本物のサイトのURLを掴む"""
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    try:
        r = requests.get(google_url, headers=headers, timeout=10, allow_redirects=True)
        return r.url
    except:
        return google_url

def extract_image_by_site(url, source_name):
    """私たちが解析した、各サイトごとの専用画像抽出ロジック"""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # サイトごとの出し分け（あの時の職人技ロジック）
        if "ナタリー" in source_name:
            # ナタリー専用：メイン画像クラスを優先
            img = soup.select_one('meta[property="og:image"]') or soup.select_one('.NA_article_img img')
        elif "オリコン" in source_name:
            # オリコン専用：記事内の画像
            img = soup.select_one('meta[property="og:image"]') or soup.select_one('.article-img img')
        elif "モデルプレス" in source_name:
            # モデルプレス専用：高画質画像
            img = soup.select_one('meta[property="og:image"]') or soup.select_one('.mdpr-article__img img')
        elif "MANTANWEB" in source_name:
            # MANTAN専用
            img = soup.select_one('meta[property="og:image"]') or soup.select_one('.article__img img')
        elif "マイナビ" in source_name:
            # マイナビ専用
            img = soup.select_one('meta[property="og:image"]') or soup.select_one('.article-body__img img')
        else:
            img = soup.select_one('meta[property="og:image"]')
            
        if img:
            content = img.get("content") or img.get("src")
            if content and content.startswith('http'):
                return content
    except:
        pass
    return ""

def fetch_all_news():
    # 5大サイトそれぞれを巡回する
    sites = [
        {"name": "ナタリー", "domain": "natalie.mu"},
        {"name": "オリコン", "domain": "oricon.co.jp"},
        {"name": "モデルプレス", "domain": "mdpr.jp"},
        {"name": "MANTANWEB", "domain": "mantan-web.jp"},
        {"name": "マイナビ", "domain": "news.mynavi.jp"}
    ]
    
    all_results = []
    for site in sites:
        print(f"\n--- {site['name']} を攻略中 ---")
        rss_url = f"https://news.google.com/rss/search?q=site:{site['domain']} 永瀬廉&hl=ja&gl=JP&ceid=JP:ja"
        try:
            r = requests.get(rss_url, timeout=10)
            soup = BeautifulSoup(r.content, "xml")
            items = soup.find_all("item")[:10] # 各サイト最新10件
            
            for i in items:
                title = i.title.text
                g_link = i.link.text
                print(f"  解析: {title[:15]}...")
                
                real_url = get_real_url(g_link)
                img = extract_image_by_site(real_url, site['name'])
                
                if img: print(f"    [成功] 画像を確保")
                
                p_date = email.utils.parsedate_to_datetime(i.pubDate.text)
                all_results.append({
                    "title": title,
                    "url": real_url,
                    "date": p_date.strftime('%Y-%m-%d %H:%M'),
                    "source": site['name'],
                    "img": img
                })
                time.sleep(1)
        except:
            continue
    return all_results

def update_json(new_news):
    # 既存のYouTubeやタイトル下画像を壊さないよう読み込む
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"images": [], "featured": {}, "regulars": [], "news": []}

    # ニュースだけを入れ替え
    data["news"] = new_news
    # 日時順に並び替え
    data["news"].sort(key=lambda x: x['date'], reverse=True)
    # 最大30件
    data["news"] = data["news"][:30]

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了: 30件のニュースを整理しました。")

if __name__ == "__main__":
    update_json(fetch_all_news())
