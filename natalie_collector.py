import requests
from bs4 import BeautifulSoup
import re
import time

def collect():
    print("🎬 映画ナタリー：詳細ページの '.NA_article_date' を解析中...")
    # 永瀬さんのニュース一覧
    list_url = "https://natalie.mu/eiga/news/list/artist_id/70325"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        # 1. まず一覧を取得
        res = requests.get(list_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 記事リンクを抽出（NA_card または aタグの href から）
        links = []
        for a in soup.find_all('a', href=True):
            if '/eiga/news/' in a['href'] and a.get_text(strip=True):
                full_url = "https://natalie.mu" + a['href'] if a['href'].startswith('/') else a['href']
                if full_url not in [l['url'] for l in links]:
                    links.append({'url': full_url, 'title': a.get_text(strip=True)})
        
        articles = []
        # 2. 上位5件だけ、ゆっくりと詳細を見に行く
        for target in links[:5]:
            # 「永瀬廉」が含まれる記事のみ
            if "永瀬廉" not in target['title']: continue
            
            print(f"🕵️ 真実の日付を確認中: {target['title'][:12]}...")
            
            # 人間が読む間隔（3秒待機）
            time.sleep(3)
            
            try:
                detail_res = requests.get(target['url'], headers=headers, timeout=10)
                detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                
                # あなたが見つけてくれたクラス名を指定
                date_el = detail_soup.select_one('.NA_article_date')
                if date_el:
                    raw_date = date_el.get_text(strip=True)
                    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', raw_date)
                    date_clean = f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}" if m else "2026-02-15"
                else:
                    date_clean = "2026-02-15"
                
                # 画像も詳細ページから
                og_img = detail_soup.find("meta", property="og:image")
                thumbnail = og_img["content"] if og_img else ""
                
                articles.append({
                    'site_name': '映画ナタリー',
                    'title': target['title'],
                    'link': target['url'],
                    'date': date_clean,
                    'thumbnail': thumbnail
                })
            except:
                continue
                
            if len(articles) >= 5: break
            
        return articles
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []
