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
            p_date = email.utils.parsedate_to_datetime(i.pubDate.text)
            res.append({
                "title": i.title.text,
                "url": i.link.text,
                "date": p_date.strftime('%Y-%m-%d %H:%M'),
                "source": i.source.text if i.source else "News",
                "img": "" 
            })
        return res
    except:
        return []

def update_news_only(new_news):
    if not os.path.exists(DATA_FILE):
        print("エラー: news.jsonが見つかりません。ステップ1をやり直してください。")
        return

    # 1. 既存の「画像」や「動画」の入った本物のデータを読み込む
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    # 2. 「news」の部分だけを入れ替える（imagesやfeaturedはそのまま残る）
    full_data["news"] = new_news
    full_data["news"].sort(key=lambda x: x['date'], reverse=True)
    full_data["news"] = full_data["news"][:30] # 最新30件に制限

    # 3. 保存
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    print(f"成功: 画像と動画を保持したまま、ニュース{len(full_data['news'])}件を更新しました。")

if __name__ == "__main__":
    update_news_only(fetch_broad_news())
