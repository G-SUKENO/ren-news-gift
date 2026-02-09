import requests
from bs4 import BeautifulSoup
import re

def collect():
    print("📡 MOVIE WALKER PRESSを精密フィルターで抽出中...")
    items = []
    # 検索ページ
    search_url = "https://moviewalker.jp/news/search/?q=%E6%B0%B8%E7%80%AC%E5%BB%89"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    # 必須キーワード
    keywords = ["永瀬廉", "King & Prince", "キンプリ"]

    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 検索結果の記事カードをすべて取得
        # MOVIE WALKERの検索結果は各記事が p-news-list__item クラスなどで囲まれています
        articles = soup.select('.p-news-list__item')
        
        for article in articles:
            a_tag = article.find('a')
            if not a_tag: continue
            
            link = "https://moviewalker.jp" + a_tag['href'] if a_tag['href'].startswith('/') else a_tag['href']
            
            # タイトルの取得と検証
            title_elem = article.select_one('.p-news-list__item-title') or a_tag
            raw_title = title_elem.get_text(strip=True)
            
            # 【重要】タイトルにキーワードが含まれているか厳格にチェック
            if not any(k in raw_title for k in keywords):
                # タイトルになければスキップ（これで無関係な記事を排除）
                continue
            
            print(f"🎯 永瀬廉関連記事を特定: {raw_title[:15]}...")
            
            try:
                # 詳細ページから画像(OGP)を取得
                res_d = requests.get(link, headers=headers, timeout=5)
                soup_d = BeautifulSoup(res_d.text, 'html.parser')
                
                og_img = soup_d.find('meta', property='og:image')
                thumbnail = og_img['content'] if og_img else ""
                
                date_tag = soup_d.find('time')
                date = date_tag.get_text(strip=True) if date_tag else ""

                items.append({
                    "site_name": "MOVIE WALKER",
                    "title": raw_title,
                    "link": link,
                    "date": date,
                    "thumbnail": thumbnail
                })
                print(f"✅ MOVIE WALKER抽出成功: {raw_title[:10]}")
            except:
                continue
            
            if len(items) >= 5: break

    except Exception as e:
        print(f"❌ MOVIE WALKER解析失敗: {e}")
        
    return items
