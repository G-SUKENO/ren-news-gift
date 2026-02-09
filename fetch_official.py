import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_news():
    url = "https://www.universal-music.co.jp/king-and-prince/news/"
    # ブラウザになりすますための情報をさらに強化
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        new_articles = []
        
        # 1. リンク(aタグ)をベースに、親要素や子要素からタイトルと日付を強引に抜く
        # 今のユニバーサルの構造を網羅的に探す
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            # ニュース詳細へのリンクと思われるものに絞る
            if '/king-and-prince/news/20' in href:
                # 親要素や自分自身からタイトルを探す
                # title, h3, p, span, などを順番にチェック
                title_elem = link.select_one('.title, h3, span, .text')
                title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
                
                # 日付を探す
                date_elem = link.find_previous('p', class_='date') or link.select_one('.date, time')
                date_str = date_elem.get_text(strip=True) if date_elem else "2026.02.06" # 取れなければ仮

                if title and len(title) > 5: # 短すぎるゴミデータを除外
                    full_url = href if href.startswith('http') else "https://www.universal-music.co.jp" + href
                    
                    if not any(a['url'] == full_url for a in new_articles):
                        new_articles.append({
                            "title": title,
                            "url": full_url,
                            "date": date_str,
                            "image": "images/photo_9.jpg",
                            "site_name": "Official"
                        })

        # 保存処理
        data = {"news": [], "shorts": []}
        if os.path.exists('news.json'):
            with open('news.json', 'r', encoding='utf-8') as f:
                try: data = json.load(f)
                except: pass

        if new_articles:
            # 日付順（っぽいもの）に並べ替え（簡易的）
            new_articles.sort(key=lambda x: x['date'], reverse=True)
            data['news'] = new_articles[:50]
            print(f"✅ 成功: {len(data['news'])}件の記事を抽出しました。")
        else:
            print("⚠️ まだ見つかりません。HTMLのダンプを確認します。")

        with open('news.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"❌ エラー発生: {e}")

if __name__ == "__main__":
    fetch_news()
