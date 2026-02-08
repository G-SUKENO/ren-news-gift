import requests
from bs4 import BeautifulSoup
import json
import re
import time

def fetch_universal_news():
    base_url = "https://www.universal-music.co.jp/king-and-prince/news/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(base_url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        # 一覧からリンクを抽出
        articles = soup.find_all('a', href=re.compile(r'/king-and-prince/news/\d+'))
        
        for a_tag in articles[:8]:
            title = a_tag.get_text(strip=True)
            if not title or len(title) < 10: continue
            
            detail_url = a_tag['href']
            if not detail_url.startswith('http'):
                detail_url = "https://www.universal-music.co.jp" + detail_url

            print(f"詳細解析中: {title[:15]}...")
            time.sleep(1) # サーバーへの礼儀
            
            try:
                detail_res = requests.get(detail_url, headers=headers)
                detail_res.encoding = detail_res.apparent_encoding
                detail_soup = BeautifulSoup(detail_res.text, 'html.parser')
                
                # 1. 真の投稿日を詳細ページから抽出
                # ユニバーサルの詳細ページにある timeタグや .date クラスを狙い撃ち
                date_node = detail_soup.select_one('time') or detail_soup.select_one('.date') or detail_soup.select_one('.entry-date')
                true_date = date_node.get_text(strip=True) if date_node else ""
                
                # もし詳細ページになければ、一覧ページの親要素から探す補助ロジック
                if not true_date:
                    parent = a_tag.find_parent(['li', 'div', 'article'])
                    fallback_date = parent.find(string=re.compile(r'\d{4}\.\d{2}\.\d{2}')) if parent else None
                    true_date = fallback_date.strip() if fallback_date else ""

                # 2. 本物の画像を詳細ページから抽出
                img_node = detail_soup.select_one('.entry-content img') or detail_soup.find('meta', property='og:image')
                if img_node:
                    img_url = img_node.get('src') or img_node.get('content')
                else:
                    img_url = "images/photo_9.jpg"

                if not any(n['url'] == detail_url for n in news_list):
                    news_list.append({
                        "site_name": "Official",
                        "date": true_date,
                        "title": title,
                        "url": detail_url,
                        "image": img_url
                    })
            except Exception as e:
                print(f"詳細解析エラー: {e}")

        return news_list
    except Exception as e:
        print(f"一覧取得エラー: {e}")
        return []

if __name__ == "__main__":
    new_articles = fetch_universal_news()
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {"news": [], "shorts": []}

    data["news"] = new_articles
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n完了：公式ニュース {len(new_articles)}件（真の日付・画像抽出済）")
