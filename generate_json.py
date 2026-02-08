import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime
import email.utils

DATA_FILE = 'news.json'

def fetch_broad_news():
    # GoogleニュースRSS（永瀬廉）を利用して幅広いソースから取得
    url = "https://news.google.com/rss/search?q=%E6%B0%B8%E7%80%AC%E5%BB%89&hl=ja&gl=JP&ceid=JP:ja"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        res = []
        for i in items:
            # 投稿日時（pubDate）を解析して並び替え可能な形式に変換
            pub_date_str = i.pubDate.text
            parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
            
            res.append({
                "title": i.title.text,
                "url": i.link.text,
                "date": parsed_date.strftime('%Y-%m-%d %H:%M'), # 投稿日時
                "source": i.source.text if i.source else "News",
                "img": "" # RSSからは画像取得が難しいため空（index.htmlのplaceholderで対応）
            })
        return res
    except Exception as e:
        print(f"取得エラー: {e}")
        return []

def update_json(new_data):
    # index.htmlが期待する構造（{"news": [...]}）に合わせて保存
    final_data = {"news": []}
    
    # 既存データの読み込み（過去記事を保持したい場合）
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: 
                old_data = json.load(f)
                final_data["news"] = old_data.get("news", [])
            except: pass

    # 重複排除と追加
    links = {n['url'] for n in final_data["news"]}
    added = 0
    for item in new_data:
        if item['url'] not in links:
            final_data["news"].append(item)
            added += 1
    
    # 【重要】記事の「投稿日時」順に並び替え（新しいものが上）
    final_data["news"].sort(key=lambda x: x['date'], reverse=True)
    
    # 最新の30件に絞る（または必要に応じて全件保持）
    # final_data["news"] = final_data["news"][:30]

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    print(f"完了: {added}件の新しい記事を追加（現在合計: {len(final_data['news'])}件）")

if __name__ == "__main__":
    update_json(fetch_broad_news())
