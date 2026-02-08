import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
import email.utils

DATA_FILE = 'news.json'

def fetch_broad_news():
    url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        res = []
        for i in items:
            pub_date_str = i.pubDate.text
            parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
            res.append({
                "title": i.title.text,
                "url": i.link.text,
                "date": parsed_date.strftime('%Y-%m-%d %H:%M'),
                "source": i.source.text if i.source else "News",
                "img": "" # RSSからは取得できないため空
            })
        return res
    except Exception as e:
        print(f"取得エラー: {e}")
        return []

def update_json(new_news):
    # 1. 現在のデータを読み込む（画像や動画のリストを保持するため）
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                full_data = json.load(f)
            except:
                full_data = {"images": [], "featured": {}, "regulars": [], "news": []}
    else:
        full_data = {"images": [], "featured": {}, "regulars": [], "news": []}

    # 2. ニュース部分だけを更新（既存の画像などはそのまま）
    full_data["news"] = new_news
    
    # 投稿日時順に並び替え
    full_data["news"].sort(key=lambda x: x['date'], reverse=True)

    # 3. 保存
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    print(f"完了: ニュースを{len(new_news)}件更新しました。画像と動画のデータは保持されました。")

if __name__ == "__main__":
    update_json(fetch_broad_news())
