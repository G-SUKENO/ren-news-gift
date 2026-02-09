import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin

def fetch_news():
    # 巡回ターゲット（全方位カバー）
    targets = [
        {"name": "Official", "url": "https://www.universal-music.co.jp/king-and-prince/news/"},
        {"name": "Natalie", "url": "https://natalie.mu/music/tag/1043"},
        {"name": "Oricon", "url": "https://www.oricon.co.jp/prof/717882/news/"},
        {"name": "Billboard", "url": "https://www.billboard-japan.com/search/news?word=King+%26+Prince"},
        {"name": "ModelPress", "url": "https://mdpr.jp/tag/11500"},
        {"name": "Edgeline", "url": "https://www.edgeline-tokyo.com/tag/king-prince"},
        {"name": "MovieWalker", "url": "https://moviewalker.jp/tag/38283/"},
        {"name": "RealSound", "url": "https://realsound.jp/tag/king-prince"}
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    scraped_articles = []

    for target in targets:
        try:
            print(f"🧐 {target['name']} をチェック中...")
            res = requests.get(target['url'], headers=headers, timeout=12)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 各サイトの構造から記事を抽出（セレクタをより広範囲に設定）
            items = soup.select('article, .news-list-item, li[class*="news"], .u-main-v2__item, .mdpr-articleCard, .news-card, .list-item, .post-item')
            
            for item in items[:15]: # 各サイト上位15件をチェック
                link_tag = item.find('a', href=True)
                # タイトルを探す（クラス名を網羅）
                title_tag = item.select_one('.title, h3, .h3, .text, .mdpr-articleCard__title, .list-item__title, .entry-title')
                
                if link_tag and title_tag:
                    title = title_tag.get_text(strip=True)
                    # 短すぎる、または長すぎるゴミデータ、SNSシェアリンク等を除外
                    if len(title) < 10 or "Twitter" in title or "Facebook" in title:
                        continue

                    full_url = urljoin(target['url'], link_tag['href'])
                    
                    scraped_articles.append({
                        "title": title,
                        "url": full_url,
                        "date": datetime.now().strftime("%Y.%m.%d"),
                        "image": "images/photo_9.jpg",
                        "site_name": target['name']
                    })
        except Exception as e:
            print(f"⚠️ {target['name']} でエラー: {e}")
            continue

    # --- 50件維持 & 重複排除ロジック ---
    data = {"news": [], "shorts": []}
    if os.path.exists('news.json'):
        with open('news.json', 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: pass

    existing_news = data.get('news', [])
    
    # 今回取得した記事を、古い順からチェックして既存リストの先頭に「差し込み」
    # URLで重複を確認するので、同じ記事は二度入りません
    new_count = 0
    for article in reversed(scraped_articles):
        if not any(e['url'] == article['url'] for e in existing_news):
            existing_news.insert(0, article)
            new_count += 1

    # 常に最新50件のみを保持（古いものは自動削除）
    data['news'] = existing_news[:50]

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 成功: 新たに {new_count} 件の記事を追加しました。")
    print(f"📦 現在のストック合計: {len(data['news'])} 件")

if __name__ == "__main__":
    fetch_news()
